def check_revenue_vs_receivables(revenue_growth, receivables_growth):
    if revenue_growth is None or receivables_growth is None:
        return {
            "flag": False,
            "message": "Not enough data to analyze revenue and receivables."
        }

    difference = receivables_growth - revenue_growth

    if difference >= 10:
        return {
            "flag": True,
            "message": (
                f"Receivables are growing {difference:.2f} "
                "percentage points faster than revenue."
            )
        }

    return {
        "flag": False,
        "message": (
            "Receivables growth is not significantly higher "
            "than revenue growth."
        )
    }


def check_cash_flow_conversion(cash_flow_conversion):
    if cash_flow_conversion is None:
        return {
            "flag": False,
            "message": "Not enough data to analyze cash flow conversion."
        }

    if cash_flow_conversion < 80:
        return {
            "flag": True,
            "message": (
                f"Operating cash flow is only "
                f"{cash_flow_conversion:.2f}% of net income."
            )
        }

    return {
        "flag": False,
        "message": (
            "Operating cash flow is reasonably strong "
            "relative to net income."
        )
    }


def check_inventory_vs_revenue(inventory_growth, revenue_growth):
    if inventory_growth is None or revenue_growth is None:
        return {
            "flag": False,
            "message": "Not enough data to analyze inventory and revenue."
        }

    difference = inventory_growth - revenue_growth

    if difference >= 10:
        return {
            "flag": True,
            "message": (
                f"Inventory is growing {difference:.2f} "
                "percentage points faster than revenue."
            )
        }

    return {
        "flag": False,
        "message": (
            "Inventory growth is not significantly higher "
            "than revenue growth."
        )
    }


def check_liabilities_vs_assets(liabilities_growth, assets_growth):
    if liabilities_growth is None or assets_growth is None:
        return {
            "flag": False,
            "message": "Not enough data to analyze liabilities and assets."
        }

    difference = liabilities_growth - assets_growth

    if difference >= 10:
        return {
            "flag": True,
            "message": (
                f"Liabilities are growing {difference:.2f} "
                "percentage points faster than assets."
            )
        }

    return {
        "flag": False,
        "message": (
            "Liabilities growth is not significantly higher "
            "than assets growth."
        )
    }


def check_dso_change(dso_change):
    if dso_change is None:
        return {
            "flag": False,
            "message": "Not enough data to analyze DSO."
        }

    if dso_change >= 10:
        return {
            "flag": True,
            "message": (
                f"DSO increased by {dso_change:.2f}% "
                "compared with the previous year."
            )
        }

    return {
        "flag": False,
        "message": (
            "DSO has not increased significantly "
            "compared with the previous year."
        )
    }


def check_fcf_conversion(fcf_conversion):
    if fcf_conversion is None:
        return {
            "flag": False,
            "message": "Not enough data to analyze free cash flow."
        }

    if fcf_conversion < 70:
        return {
            "flag": True,
            "message": (
                f"Free cash flow is only "
                f"{fcf_conversion:.2f}% of net income."
            )
        }

    return {
        "flag": False,
        "message": (
            "Free cash flow is reasonably strong "
            "relative to net income."
        )
    }


def check_current_ratio(current_ratio):
    if current_ratio is None:
        return {
            "flag": False,
            "message": "Not enough data to analyze current ratio."
        }

    if current_ratio < 1:
        return {
            "flag": True,
            "message": (
                f"Current ratio is {current_ratio:.2f}, "
                "indicating current liabilities exceed current assets."
            )
        }

    return {
        "flag": False,
        "message": (
            "Current ratio indicates reasonable "
            "short-term liquidity."
        )
    }


def check_debt_growth(debt_growth):
    if debt_growth is None:
        return {
            "flag": False,
            "message": "Not enough data to analyze debt growth."
        }

    if debt_growth >= 10:
        return {
            "flag": True,
            "message": (
                f"Debt increased by {debt_growth:.2f}% "
                "compared with the previous year."
            )
        }

    return {
        "flag": False,
        "message": "Debt growth does not appear significantly elevated."
    }