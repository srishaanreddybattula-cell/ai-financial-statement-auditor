RISK_WEIGHTS = {
    "revenue_quality": 20,
    "accrual_quality": 15,
    "cash_flow_quality": 15,
    "working_capital": 15,
    "accounting_policy_risk": 15,
    "leverage_liquidity": 10,
    "peer_deviation": 10
}


def calculate_risk_score(risk_dimensions):
    score = 0

    for dimension, weight in RISK_WEIGHTS.items():
        risk_level = risk_dimensions.get(dimension, 0)

        if risk_level < 0:
            risk_level = 0

        if risk_level > 100:
            risk_level = 100

        score += (risk_level / 100) * weight

    return round(score, 2)


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