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
    """Summarize available annual financial metrics for screening coverage."""
    available = []
    missing = []

    for key, label in REQUIRED_METRICS.items():
        values = financial_data.get(key, [])
        if values:
            available.append(label)
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

    return {
        "coverage_percent": round(coverage, 2),
        "available": available,
        "missing": missing,
        "status": status,
    }
