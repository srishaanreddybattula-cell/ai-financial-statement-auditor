def assess_policy_risk(accounting_topics):
    """Score accounting-policy disclosures only when multiple risk attributes coincide.

    Normal disclosure of an accounting policy is not itself treated as elevated risk.
    """
    if not accounting_topics:
        return None

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


def _threshold_risk(value, low_threshold, high_threshold, higher_is_riskier):
    if value is None:
        return None

    if higher_is_riskier:
        if value >= high_threshold:
            return 40
        if value >= low_threshold:
            return 20
    else:
        if value <= high_threshold:
            return 40
        if value <= low_threshold:
            return 20

    return 0


def assess_risk_dimensions(indicators):
    """Map screening indicators into distinct risk dimensions.

    ``None`` means the required underlying data was unavailable. It is kept
    separate from 0, which means the available data did not trigger a rule.
    """
    revenue_quality = 0
    working_capital = 0

    if indicators.get("revenue_vs_receivables", {}).get("flag"):
        revenue_quality += 50

    if indicators.get("dso", {}).get("flag"):
        revenue_quality += 30

    if indicators.get("inventory_vs_revenue", {}).get("flag"):
        working_capital += 40

    leverage_liquidity = 0
    ratio_risk = _threshold_risk(
        indicators.get("current_ratio", {}).get("value"),
        low_threshold=0.8,
        high_threshold=1.0,
        higher_is_riskier=False,
    )
    if ratio_risk is not None:
        leverage_liquidity += ratio_risk

    debt_risk = _threshold_risk(
        indicators.get("debt_to_assets", {}).get("value"),
        low_threshold=0.30,
        high_threshold=0.50,
        higher_is_riskier=True,
    )
    if debt_risk is not None:
        leverage_liquidity += debt_risk

    liabilities_risk = _threshold_risk(
        indicators.get("liabilities_to_assets", {}).get("value"),
        low_threshold=0.60,
        high_threshold=0.80,
        higher_is_riskier=True,
    )
    if liabilities_risk is not None:
        leverage_liquidity += liabilities_risk

    return {
        "revenue_quality": min(revenue_quality, 100),
        "accrual_quality": None,
        "cash_flow_quality": None,
        "working_capital": min(working_capital, 100),
        "accounting_policy_risk": None,
        "leverage_liquidity": min(leverage_liquidity, 100),
        "peer_deviation": None,
    }
