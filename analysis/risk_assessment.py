def assess_policy_risk(accounting_topics):
    """Score accounting-policy disclosures only when multiple risk attributes coincide.

    Normal disclosure of an accounting policy is not itself treated as elevated risk.
    """
    if not accounting_topics:
        return 0

    risk_score = 0

    for analysis in accounting_topics.values():
        judgment = analysis.get("judgment", False)
        uncertainty = analysis.get("uncertainty", False)
        material_impact = analysis.get("material_impact", False)

        if judgment and uncertainty and material_impact:
            risk_score += 20
        elif judgment and uncertainty:
            risk_score += 10

    return min(risk_score, 100)


def assess_risk_dimensions(indicators):
    revenue_quality = 0
    accrual_quality = 0
    cash_flow_quality = 0
    working_capital = 0
    accounting_policy_risk = 0
    leverage_liquidity = 0
    peer_deviation = 0

    if indicators["revenue_vs_receivables"]["flag"]:
        revenue_quality += 50

    if indicators["dso"]["flag"]:
        revenue_quality += 30

    if indicators["cash_flow"]["flag"]:
        cash_flow_quality += 60
        accrual_quality += 40

    if indicators["free_cash_flow"]["flag"]:
        cash_flow_quality += 30

    if indicators["inventory_vs_revenue"]["flag"]:
        working_capital += 40

    if indicators["current_ratio"]["flag"]:
        leverage_liquidity += 40
        working_capital += 20

    if indicators["debt"]["flag"]:
        leverage_liquidity += 40

    if indicators["liabilities_vs_assets"]["flag"]:
        leverage_liquidity += 30

    return {
        "revenue_quality": min(revenue_quality, 100),
        "accrual_quality": min(accrual_quality, 100),
        "cash_flow_quality": min(cash_flow_quality, 100),
        "working_capital": min(working_capital, 100),
        "accounting_policy_risk": accounting_policy_risk,
        "leverage_liquidity": min(leverage_liquidity, 100),
        "peer_deviation": peer_deviation
    }
