def detect_growth_anomalies(trend, threshold=20):
    anomalies = []

    for item in trend:
        growth = item.get("growth")

        if growth is None:
            continue

        if abs(growth) >= threshold:
            anomalies.append({
                "year": item["year"],
                "growth": growth,
                "message": (
                    f"Revenue growth of {growth:.2f}% "
                    "is unusually large."
                )
            })

    return anomalies

def detect_receivables_anomalies(
    revenue_growth,
    receivables_growth,
    threshold=10
):
    if revenue_growth is None or receivables_growth is None:
        return None

    difference = receivables_growth - revenue_growth

    if difference >= threshold:
        return {
            "flag": True,
            "difference": difference,
            "message": (
                f"Receivables growth exceeded revenue growth "
                f"by {difference:.2f} percentage points."
            )
        }

    return {
        "flag": False,
        "difference": difference,
        "message": (
            "Receivables growth is not significantly higher "
            "than revenue growth."
        )
    }