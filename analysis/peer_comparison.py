def _median(values):
    values = sorted(values)
    if not values:
        return None
    middle = len(values) // 2
    if len(values) % 2:
        return values[middle]
    return (values[middle - 1] + values[middle]) / 2


def _mad(values, center):
    deviations = [abs(value - center) for value in values]
    return _median(deviations)


def _robust_z_score(value, peer_values):
    if value is None or len(peer_values) < 2:
        return None

    center = _median(peer_values)
    mad = _mad(peer_values, center)

    if center is None or mad in (None, 0):
        return None

    return 0.6745 * (value - center) / mad


def calculate_peer_deviation(company_metrics, peer_metrics):
    """Compare selected risk-related metrics with a peer group.

    The function returns a 0-100 screening risk level based on robust
    deviations from the peer median. It does not establish that a company
    has an accounting error or misconduct.
    """
    if not peer_metrics:
        return {
            "risk_score": 0,
            "peer_count": 0,
            "metrics": {},
            "message": "No peer data was available for comparison."
        }

    metric_directions = {
        "receivables_to_revenue": "higher",
        "dso": "higher",
        "accrual_ratio": "higher",
        "current_ratio": "lower",
        "ocf_conversion": "lower",
    }

    metric_results = {}
    risk_components = []

    for metric, direction in metric_directions.items():
        company_value = company_metrics.get(metric)
        peer_values = [
            peer.get(metric)
            for peer in peer_metrics
            if peer.get(metric) is not None
        ]

        if company_value is None or len(peer_values) < 2:
            continue

        median = _median(peer_values)
        z_score = _robust_z_score(company_value, peer_values)

        if median is None:
            continue

        if direction == "higher":
            directional_z = z_score
        else:
            directional_z = -z_score

        if directional_z is None:
            risk_level = 0
        elif directional_z <= 0:
            risk_level = 0
        elif directional_z >= 3:
            risk_level = 100
        else:
            risk_level = (directional_z / 3) * 100

        metric_results[metric] = {
            "company_value": company_value,
            "peer_median": median,
            "z_score": round(z_score, 2) if z_score is not None else None,
            "risk_level": round(risk_level, 2),
        }
        risk_components.append(risk_level)

    if not risk_components:
        return {
            "risk_score": 0,
            "peer_count": len(peer_metrics),
            "metrics": metric_results,
            "message": "Not enough comparable peer metrics were available."
        }

    risk_score = sum(risk_components) / len(risk_components)

    return {
        "risk_score": round(min(max(risk_score, 0), 100), 2),
        "peer_count": len(peer_metrics),
        "metrics": metric_results,
        "message": (
            "Peer deviation measures how unusual selected risk-related metrics "
            "are relative to the peer median. It is a screening signal, not a "
            "conclusion about accounting quality."
        ),
    }
