def normalize_annual_data(data):
    if not data:
        return []

    yearly_data = {}

    for item in data:
        year = item.get("year")

        if year is None:
            continue

        if year not in yearly_data:
            yearly_data[year] = item
        else:
            current_filed = item.get("filed", "")
            existing_filed = yearly_data[year].get("filed", "")

            if current_filed > existing_filed:
                yearly_data[year] = item

    return sorted(
        yearly_data.values(),
        key=lambda x: x["year"]
    )