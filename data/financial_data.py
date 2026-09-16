from datetime import date


def _fact_metadata(value):
    return {
        "form": value.get("form"),
        "accn": value.get("accn"),
        "accession_number": value.get("accn"),
        "frame": value.get("frame"),
    }


def get_fact(company_facts, fact_name):
    try:
        fact = company_facts["facts"]["us-gaap"][fact_name]
    except KeyError:
        return []

    results = []

    for unit, values in fact["units"].items():
        yearly_values = {}

        for value in values:
            if value.get("form") != "10-K":
                continue

            end = value.get("end")
            filed = value.get("filed")

            if not end or not filed:
                continue

            start = value.get("start")

            # Flow statement values must cover approximately one full year.
            if start:
                start_date = date.fromisoformat(start)
                end_date = date.fromisoformat(end)
                days = (end_date - start_date).days

                if not 350 <= days <= 380:
                    continue

            year = int(end[:4])
            record = {
                "year": year,
                "value": value.get("val"),
                "filed": filed,
                "start": start,
                "end": end,
                **_fact_metadata(value),
            }

            if year not in yearly_values:
                yearly_values[year] = record
            elif filed > yearly_values[year]["filed"]:
                yearly_values[year] = record

        results.extend(yearly_values.values())

    return sorted(
        results,
        key=lambda x: x["year"]
    )


def get_net_income(company_facts):
    tags = [
        "ProfitLoss",
        "NetIncomeLoss"
    ]

    for tag in tags:
        if tag in company_facts["facts"]["us-gaap"]:
            result = get_fact(company_facts, tag)

            if result:
                return result

    return []


def get_capex(company_facts):
    try:
        fact = company_facts["facts"]["us-gaap"][
            "PaymentsToAcquirePropertyPlantAndEquipment"
        ]
    except KeyError:
        return []

    yearly_results = {}

    for unit, values in fact["units"].items():
        for value in values:
            if value.get("form") != "10-K":
                continue

            start = value.get("start")
            end = value.get("end")
            filed = value.get("filed")

            if not start or not end or not filed:
                continue

            start_date = date.fromisoformat(start)
            end_date = date.fromisoformat(end)

            days = (end_date - start_date).days

            if not 350 <= days <= 380:
                continue

            year = end_date.year
            record = {
                "year": year,
                "value": value.get("val"),
                "filed": filed,
                "start": start,
                "end": end,
                **_fact_metadata(value),
            }

            if year not in yearly_results:
                yearly_results[year] = record
            elif filed > yearly_results[year]["filed"]:
                yearly_results[year] = record

    return sorted(
        yearly_results.values(),
        key=lambda x: x["year"]
    )


def get_debt(company_facts):
    us_gaap = company_facts["facts"]["us-gaap"]

    current_tag = "LongTermDebtCurrent"
    noncurrent_tag = "LongTermDebtNoncurrent"

    yearly_results = {}

    for tag in [current_tag, noncurrent_tag]:
        if tag not in us_gaap:
            continue

        fact = us_gaap[tag]

        for unit, values in fact["units"].items():
            for value in values:
                if value.get("form") != "10-K":
                    continue

                end = value.get("end")
                filed = value.get("filed")

                if not end or not filed:
                    continue

                year = int(end[:4])

                if year not in yearly_results:
                    yearly_results[year] = {
                        "year": year,
                        "current": 0,
                        "noncurrent": 0,
                        "filed": filed,
                        "end": end,
                        "accn": value.get("accn"),
                        "form": value.get("form"),
                    }

                if tag == current_tag:
                    yearly_results[year]["current"] = value.get("val", 0)

                elif tag == noncurrent_tag:
                    yearly_results[year]["noncurrent"] = value.get("val", 0)

                if filed > yearly_results[year]["filed"]:
                    yearly_results[year]["filed"] = filed
                    yearly_results[year]["accn"] = value.get("accn")
                    yearly_results[year]["form"] = value.get("form")

    for year, item in yearly_results.items():
        item["value"] = item["current"] + item["noncurrent"]

    return sorted(
        yearly_results.values(),
        key=lambda x: x["year"]
    )


def get_goodwill(company_facts):
    """Extract annual goodwill balances from 10-K filings when reported."""
    return get_fact(company_facts, "Goodwill")


def get_financial_data(company_facts):
    return {
        "revenue": get_fact(
            company_facts,
            "RevenueFromContractWithCustomerExcludingAssessedTax"
        ),

        "net_income": get_net_income(
            company_facts
        ),

        "assets": get_fact(
            company_facts,
            "Assets"
        ),

        "cash": get_fact(
            company_facts,
            "CashAndCashEquivalentsAtCarryingValue"
        ),

        "liabilities": get_fact(
            company_facts,
            "Liabilities"
        ),

        "debt": get_debt(
            company_facts
        ),

        "receivables": get_fact(
            company_facts,
            "AccountsReceivableNetCurrent"
        ),

        "inventory": get_fact(
            company_facts,
            "InventoryNet"
        ),

        "goodwill": get_goodwill(
            company_facts
        ),

        "operating_cash_flow": get_fact(
            company_facts,
            "NetCashProvidedByUsedInOperatingActivities"
        ),

        "capital_expenditures": get_capex(
            company_facts
        ),

        "current_assets": get_fact(
            company_facts,
            "AssetsCurrent"
        ),

        "current_liabilities": get_fact(
            company_facts,
            "LiabilitiesCurrent"
        )
    }
