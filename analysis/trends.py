def calculate_year_over_year(data):
    if len(data) < 2:
        return []

    results = []

    for i in range(1, len(data)):
        current = data[i]
        previous = data[i - 1]

        current_value = current.get("value")
        previous_value = previous.get("value")

        if current_value is None or previous_value in (None, 0):
            continue

        change = ((current_value - previous_value) / previous_value) * 100

        results.append({
            "year": current["year"],
            "change": change
        })

    return results


def calculate_multi_year_trend(data):
    if not data:
        return {
            "first_year": None,
            "last_year": None,
            "total_change": None
        }

    first = data[0]
    last = data[-1]

    if first.get("value") in (None, 0) or last.get("value") is None:
        return {
            "first_year": first.get("year"),
            "last_year": last.get("year"),
            "total_change": None
        }

    total_change = (
        (last["value"] - first["value"])
        / first["value"]
    ) * 100

    return {
        "first_year": first["year"],
        "last_year": last["year"],
        "total_change": total_change
    }

def get_recent_years(data, years=7):
    if not data:
        return []

    sorted_data = sorted(
        data,
        key=lambda x: x.get("year", 0)
    )

    return sorted_data[-years:]
