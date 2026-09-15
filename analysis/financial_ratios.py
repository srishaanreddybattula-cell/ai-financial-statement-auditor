def calculate_growth(current, previous):
    if previous == 0:
        return None

    return ((current - previous) / previous) * 100


def calculate_profit_margin(net_income, revenue):
    if revenue == 0:
        return None

    return (net_income / revenue) * 100


def calculate_cash_flow_conversion(operating_cash_flow, net_income):
    if net_income == 0:
        return None

    return (operating_cash_flow / net_income) * 100


def calculate_fcf(operating_cash_flow, capital_expenditures):
    if operating_cash_flow is None or capital_expenditures is None:
        return None

    return operating_cash_flow - capital_expenditures


def calculate_fcf_conversion(free_cash_flow, net_income):
    if net_income == 0:
        return None

    return (free_cash_flow / net_income) * 100


def calculate_current_ratio(current_assets, current_liabilities):
    if current_liabilities == 0:
        return None

    return current_assets / current_liabilities


def calculate_receivables_to_revenue(receivables, revenue):
    if revenue == 0:
        return None

    return (receivables / revenue) * 100


def calculate_dso(receivables, revenue):
    if revenue == 0:
        return None

    return (receivables / revenue) * 365


def calculate_trend(data):
    if len(data) < 2:
        return []

    trend = []

    for i in range(1, len(data)):
        current = data[i]
        previous = data[i - 1]

        growth = calculate_growth(
            current["value"],
            previous["value"]
        )

        trend.append({
            "year": current["year"],
            "growth": growth
        })

    return trend