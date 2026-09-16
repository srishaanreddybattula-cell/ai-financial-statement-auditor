REQUIRED_METRICS = {
    "revenue": "Revenue",
    "net_income": "Net income",
    "assets": "Assets",
    "liabilities": "Liabilities",
    "receivables": "Receivables",
    "operating_cash_flow": "Operating cash flow",
    "current_assets": "Current assets",
    "current_liabilities": "Current liabilities",
}


def assess_data_quality(financial_data):
    """Summarize both metric availability and annual history needed for screening."""
    available = []
    missing = []
    insufficient_history = []
    annual_period_counts = {}

    for key, label in REQUIRED_METRICS.items():
        values = financial_data.get(key, []) or []
        years = {item.get("year") for item in values if item.get("year") is not None}
        annual_period_counts[label] = len(years)

        if values:
            available.append(label)
            if len(years) < 2:
                insufficient_history.append(label)
        else:
            missing.append(label)

    total = len(REQUIRED_METRICS)
    coverage = (len(available) / total) * 100 if total else 0

    if coverage >= 90:
        status = "High coverage"
    elif coverage >= 70:
        status = "Moderate coverage"
    else:
        status = "Limited coverage"

    screening_ready = not missing and not insufficient_history

    return {
        "coverage_percent": round(coverage, 2),
        "available": available,
        "missing": missing,
        "insufficient_history": insufficient_history,
        "annual_period_counts": annual_period_counts,
        "screening_ready": screening_ready,
        "status": status,
    }
