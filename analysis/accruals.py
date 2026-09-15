def calculate_accrual_ratio(net_income, operating_cash_flow, assets):
    if assets == 0:
        return None

    return (net_income - operating_cash_flow) / assets


def calculate_earnings_cash_difference(net_income, operating_cash_flow):
    if net_income == 0:
        return None

    return ((net_income - operating_cash_flow) / abs(net_income)) * 100


def assess_accrual_quality(net_income, operating_cash_flow, assets):
    accrual_ratio = calculate_accrual_ratio(
        net_income,
        operating_cash_flow,
        assets
    )

    earnings_cash_difference = calculate_earnings_cash_difference(
        net_income,
        operating_cash_flow
    )

    if accrual_ratio is None:
        risk_score = 0

    elif accrual_ratio > 0.10:
        risk_score = 80

    elif accrual_ratio > 0.05:
        risk_score = 50

    elif accrual_ratio > 0:
        risk_score = 25

    else:
        risk_score = 0

    return {
        "accrual_ratio": accrual_ratio,
        "earnings_cash_difference": earnings_cash_difference,
        "risk_score": risk_score
    }