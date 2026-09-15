def calculate_dso(receivables, revenue):
    if revenue == 0:
        return None
    return (receivables / revenue) * 365


def calculate_receivables_to_revenue(receivables, revenue):
    if revenue == 0:
        return None
    return (receivables / revenue) * 100


def calculate_inventory_turnover(revenue, inventory):
    if inventory == 0:
        return None
    return revenue / inventory


def calculate_days_inventory(inventory, revenue):
    if revenue == 0:
        return None
    return (inventory / revenue) * 365


def calculate_inventory_to_revenue(inventory, revenue):
    if revenue == 0:
        return None
    return (inventory / revenue) * 100


def calculate_current_ratio(current_assets, current_liabilities):
    if current_liabilities == 0:
        return None
    return current_assets / current_liabilities


def calculate_quick_ratio(current_assets, inventory, current_liabilities):
    if current_liabilities == 0:
        return None
    quick_assets = current_assets - inventory
    return quick_assets / current_liabilities


def calculate_percentage_change(current, previous):
    if previous == 0:
        return None
    return ((current - previous) / previous) * 100


def assess_working_capital(
    receivables,
    previous_receivables,
    inventory,
    previous_inventory,
    revenue,
    previous_revenue,
    current_assets,
    current_liabilities
):
    dso = calculate_dso(receivables, revenue)
    previous_dso = calculate_dso(previous_receivables, previous_revenue)

    receivables_to_revenue = calculate_receivables_to_revenue(
        receivables,
        revenue
    )

    inventory_turnover = calculate_inventory_turnover(
        revenue,
        inventory
    )

    days_inventory = calculate_days_inventory(
        inventory,
        revenue
    )

    inventory_to_revenue = calculate_inventory_to_revenue(
        inventory,
        revenue
    )

    current_ratio = calculate_current_ratio(
        current_assets,
        current_liabilities
    )

    quick_ratio = calculate_quick_ratio(
        current_assets,
        inventory,
        current_liabilities
    )

    dso_change = None
    if dso is not None and previous_dso not in (None, 0):
        dso_change = calculate_percentage_change(
            dso,
            previous_dso
        )

    receivables_growth = calculate_percentage_change(
        receivables,
        previous_receivables
    )

    inventory_growth = calculate_percentage_change(
        inventory,
        previous_inventory
    )

    revenue_growth = calculate_percentage_change(
        revenue,
        previous_revenue
    )

    risk_score = 0

    if dso_change is not None and dso_change >= 10:
        risk_score += 30

    if (
        receivables_growth is not None
        and revenue_growth is not None
        and receivables_growth - revenue_growth >= 10
    ):
        risk_score += 30

    if (
        inventory_growth is not None
        and revenue_growth is not None
        and inventory_growth - revenue_growth >= 10
    ):
        risk_score += 20

    if current_ratio is not None and current_ratio < 1:
        risk_score += 20

    risk_score = min(risk_score, 100)

    return {
        "dso": dso,
        "previous_dso": previous_dso,
        "dso_change": dso_change,
        "receivables_to_revenue": receivables_to_revenue,
        "receivables_growth": receivables_growth,
        "inventory_turnover": inventory_turnover,
        "days_inventory": days_inventory,
        "inventory_to_revenue": inventory_to_revenue,
        "inventory_growth": inventory_growth,
        "revenue_growth": revenue_growth,
        "current_ratio": current_ratio,
        "quick_ratio": quick_ratio,
        "risk_score": risk_score
    }