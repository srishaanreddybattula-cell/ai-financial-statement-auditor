RISK_WEIGHTS = {
    "revenue_quality": 20,
    "accrual_quality": 15,
    "cash_flow_quality": 15,
    "working_capital": 15,
    "accounting_policy_risk": 15,
    "leverage_liquidity": 10,
    "peer_deviation": 10,
}


def _available_dimensions(risk_dimensions):
    return {
        dimension: risk_dimensions.get(dimension)
        for dimension in RISK_WEIGHTS
        if risk_dimensions.get(dimension) is not None
    }


def calculate_score_coverage(risk_dimensions):
    """Return the share of model weight backed by available dimensions."""
    available = _available_dimensions(risk_dimensions)
    total_weight = sum(RISK_WEIGHTS.values())
    available_weight = sum(RISK_WEIGHTS[name] for name in available)
    return round((available_weight / total_weight) * 100, 2) if total_weight else 0.0


def calculate_risk_score(risk_dimensions):
    """Calculate a 0-100 score using only dimensions with available data.

    Missing dimensions are excluded from both numerator and denominator instead
    of being silently treated as zero risk. This keeps the score honest when an
    SEC filer does not expose a particular XBRL concept or peer comparison.
    """
    available = _available_dimensions(risk_dimensions)
    available_weight = sum(RISK_WEIGHTS[name] for name in available)
    if not available_weight:
        return 0.0

    score = 0.0
    for dimension, risk_level in available.items():
        risk_level = max(0.0, min(100.0, float(risk_level)))
        score += (risk_level / 100) * RISK_WEIGHTS[dimension]

    return round((score / available_weight) * 100, 2)


def calculate_score_breakdown(risk_dimensions):
    """Return the score components, including unavailable dimensions."""
    available = _available_dimensions(risk_dimensions)
    available_weight = sum(RISK_WEIGHTS[name] for name in available)
    breakdown = []

    for dimension, weight in RISK_WEIGHTS.items():
        risk_level = risk_dimensions.get(dimension)
        if risk_level is None:
            breakdown.append({
                "dimension": dimension,
                "risk_level": None,
                "weight": weight,
                "normalized_weight": round((weight / available_weight) * 100, 2) if available_weight else 0.0,
                "contribution": None,
                "available": False,
            })
            continue

        risk_level = max(0.0, min(100.0, float(risk_level)))
        normalized_weight = (weight / available_weight) * 100 if available_weight else 0.0
        contribution = (risk_level / 100) * normalized_weight
        breakdown.append({
            "dimension": dimension,
            "risk_level": risk_level,
            "weight": weight,
            "normalized_weight": round(normalized_weight, 2),
            "contribution": round(contribution, 2),
            "available": True,
        })

    return breakdown


def get_risk_category(score):
    if score <= 20:
        return "Very Low"
    elif score <= 40:
        return "Low"
    elif score <= 60:
        return "Moderate"
    elif score <= 80:
        return "High"
    else:
        return "Very High"
