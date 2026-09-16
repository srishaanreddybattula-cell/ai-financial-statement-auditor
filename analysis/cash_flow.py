def calculate_cash_flow_conversion(operating_cash_flow, net_income):
    if net_income == 0:
        return None
    return (operating_cash_flow / net_income) * 100


def calculate_free_cash_flow(operating_cash_flow, capital_expenditures):
    """Calculate FCF using the economic magnitude of capex.

    SEC/XBRL cash-outflow facts may be reported as negative values. The app
    stores the source value unchanged for provenance, so FCF must subtract the
    absolute capex amount rather than subtracting a negative outflow.
    """
    if operating_cash_flow is None or capital_expenditures is None:
        return None
    return operating_cash_flow - abs(capital_expenditures)


def calculate_fcf_conversion(free_cash_flow, net_income):
    if net_income == 0:
        return None
    return (free_cash_flow / net_income) * 100


def calculate_growth(current, previous):
    if previous in (None, 0):
        return None
    return ((current - previous) / abs(previous)) * 100


def assess_cash_flow(
    operating_cash_flow,
    previous_operating_cash_flow,
    net_income,
    previous_net_income,
    capital_expenditures,
    previous_capital_expenditures
):
    cash_flow_conversion = calculate_cash_flow_conversion(
        operating_cash_flow,
        net_income
    )

    previous_cash_flow_conversion = calculate_cash_flow_conversion(
        previous_operating_cash_flow,
        previous_net_income
    )

    free_cash_flow = calculate_free_cash_flow(
        operating_cash_flow,
        capital_expenditures
    )

    previous_free_cash_flow = calculate_free_cash_flow(
        previous_operating_cash_flow,
        previous_capital_expenditures
    )

    fcf_conversion = calculate_fcf_conversion(free_cash_flow, net_income)

    operating_cash_flow_growth = calculate_growth(
        operating_cash_flow,
        previous_operating_cash_flow
    )

    net_income_growth = calculate_growth(
        net_income,
        previous_net_income
    )

    capital_expenditures_growth = calculate_growth(
        capital_expenditures,
        previous_capital_expenditures
    )

    fcf_growth = calculate_growth(
        free_cash_flow,
        previous_free_cash_flow
    )

    conversion_change = None

    if (
        cash_flow_conversion is not None
        and previous_cash_flow_conversion is not None
    ):
        conversion_change = (
            cash_flow_conversion
            - previous_cash_flow_conversion
        )

    risk_score = 0

    if cash_flow_conversion is not None:
        if cash_flow_conversion < 80:
            risk_score += 35
        elif cash_flow_conversion < 100:
            risk_score += 15

    if fcf_conversion is not None:
        if fcf_conversion < 70:
            risk_score += 30
        elif fcf_conversion < 90:
            risk_score += 10

    if (
        operating_cash_flow_growth is not None
        and net_income_growth is not None
        and operating_cash_flow_growth < net_income_growth - 10
    ):
        risk_score += 20

    if conversion_change is not None and conversion_change <= -15:
        risk_score += 15

    risk_score = min(risk_score, 100)

    return {
        "cash_flow_conversion": cash_flow_conversion,
        "previous_cash_flow_conversion": previous_cash_flow_conversion,
        "conversion_change": conversion_change,
        "free_cash_flow": free_cash_flow,
        "previous_free_cash_flow": previous_free_cash_flow,
        "fcf_conversion": fcf_conversion,
        "operating_cash_flow_growth": operating_cash_flow_growth,
        "net_income_growth": net_income_growth,
        "capital_expenditures_growth": capital_expenditures_growth,
        "fcf_growth": fcf_growth,
        "risk_score": risk_score
    }
