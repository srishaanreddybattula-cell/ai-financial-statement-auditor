def assess_goodwill_risk(goodwill, assets, previous_goodwill=None):
    """Screen goodwill balances for material size and sharp year-over-year changes.

    A large goodwill balance is not evidence of an accounting error. This function
    only identifies balances that may warrant impairment and acquisition-accounting
    review.
    """
    if goodwill is None or assets in (None, 0):
        return {
            "risk_score": 0,
            "goodwill_to_assets": None,
            "goodwill_change": None,
            "flag": False,
            "message": "Not enough data to analyze goodwill.",
        }

    goodwill_to_assets = (goodwill / assets) * 100
    goodwill_change = None
    if previous_goodwill not in (None, 0):
        goodwill_change = ((goodwill - previous_goodwill) / abs(previous_goodwill)) * 100

    flag = goodwill_to_assets >= 20 or (
        goodwill_change is not None and goodwill_change <= -15
    )

    if flag:
        message = (
            f"Goodwill represents {goodwill_to_assets:.2f}% of total assets"
        )
        if goodwill_change is not None:
            message += f" and changed {goodwill_change:.2f}% from the prior year."
        else:
            message += "."
        message += " Review acquisitions, valuation assumptions, and impairment disclosures."
    else:
        message = "Goodwill size and year-over-year change did not trigger the current screening thresholds."

    return {
        "risk_score": 30 if flag else 0,
        "goodwill_to_assets": goodwill_to_assets,
        "goodwill_change": goodwill_change,
        "flag": flag,
        "message": message,
    }
