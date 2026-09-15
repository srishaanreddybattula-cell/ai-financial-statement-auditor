def detect_growth_anomalies(trend, threshold=20):
    anomalies = []

    for item in trend:
        growth = item.get("growth")

        if growth is None:
            continue

        if abs(growth) >= threshold:
            anomalies.append({
                "year": item["year"],
                "growth": growth,
                "message": (
                    f"Revenue growth of {growth:.2f}% "
                    "is unusually large."
                )
            })

    return anomalies


def detect_receivables_anomalies(
    revenue_growth,
    receivables_growth,
    threshold=10
):
    if revenue_growth is None or receivables_growth is None:
        return None

    difference = receivables_growth - revenue_growth

    if difference >= threshold:
        return {
            "flag": True,
            "difference": difference,
            "message": (
                f"Receivables growth exceeded revenue growth "
                f"by {difference:.2f} percentage points."
            )
        }

    return {
        "flag": False,
        "difference": difference,
        "message": (
            "Receivables growth is not significantly higher "
            "than revenue growth."
        )
    }


def detect_historical_growth_anomalies(data, minimum_years=4, z_threshold=2.0):
    """Identify annual growth rates that are unusual relative to a company's history.

    Uses a mean/std-dev z-score when enough annual observations are available.
    With fewer than minimum_years observations, no historical anomaly is reported.
    """
    if not data or len(data) < minimum_years:
        return []

    ordered = sorted(data, key=lambda item: item.get("year", 0))
    growth_rates = []

    for i in range(1, len(ordered)):
        previous = ordered[i - 1].get("value")
        current = ordered[i].get("value")

        if previous in (None, 0) or current is None:
            continue

        growth = ((current - previous) / abs(previous)) * 100
        growth_rates.append({
            "year": ordered[i]["year"],
            "growth": growth
        })

    if len(growth_rates) < 3:
        return []

    values = [item["growth"] for item in growth_rates]
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    standard_deviation = variance ** 0.5

    if standard_deviation == 0:
        return []

    anomalies = []

    for item in growth_rates:
        z_score = (item["growth"] - mean) / standard_deviation
        if abs(z_score) >= z_threshold:
            anomalies.append({
                "year": item["year"],
                "growth": item["growth"],
                "z_score": z_score,
                "historical_mean": mean,
                "historical_std": standard_deviation,
                "message": (
                    f"Growth of {item['growth']:.2f}% in {item['year']} "
                    f"was unusual relative to the company's historical pattern "
                    f"(z-score {z_score:.2f})."
                )
            })

    return anomalies


def detect_growth_acceleration(data, minimum_years=3, change_threshold=10):
    """Identify unusually large year-over-year changes in annual growth rates."""
    if not data or len(data) < minimum_years:
        return []

    ordered = sorted(data, key=lambda item: item.get("year", 0))
    growth_rates = []

    for i in range(1, len(ordered)):
        previous = ordered[i - 1].get("value")
        current = ordered[i].get("value")

        if previous in (None, 0) or current is None:
            continue

        growth_rates.append({
            "year": ordered[i]["year"],
            "growth": ((current - previous) / abs(previous)) * 100
        })

    anomalies = []

    for i in range(1, len(growth_rates)):
        previous = growth_rates[i - 1]
        current = growth_rates[i]
        change = current["growth"] - previous["growth"]

        if abs(change) >= change_threshold:
            anomalies.append({
                "year": current["year"],
                "growth": current["growth"],
                "prior_growth": previous["growth"],
                "growth_change": change,
                "message": (
                    f"Annual growth changed by {change:.2f} percentage points "
                    f"in {current['year']} compared with the prior year."
                )
            })

    return anomalies
