from datetime import date

ANNUAL_FORMS = {
    "10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A",
}


def _fact_metadata(value):
    return {
        "form": value.get("form"),
        "accn": value.get("accn"),
        "accession_number": value.get("accn"),
        "frame": value.get("frame"),
    }


def _annual_value_records(fact):
    """Convert one SEC Company Facts concept into annual observations."""
    results = []
    yearly_values = {}

    for values in fact.get("units", {}).values():
        for value in values:
            if value.get("form") not in ANNUAL_FORMS:
                continue

            end = value.get("end")
            filed = value.get("filed")
            if not end or not filed:
                continue

            start = value.get("start")
            if start:
                try:
                    start_date = date.fromisoformat(start)
                    end_date = date.fromisoformat(end)
                except ValueError:
                    continue
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

            if year not in yearly_values or filed > yearly_values[year]["filed"]:
                yearly_values[year] = record

    results.extend(yearly_values.values())
    return sorted(results, key=lambda x: x["year"])


def _get_fact_from_namespaces(company_facts, candidates):
    """Choose the best annual SEC concept across US-GAAP and IFRS.

    SEC Company Facts can expose more than one valid concept for the same
    metric. Prefer the concept with the most usable annual observations, using
    candidate order as the tie-breaker. This is important for foreign issuers
    using IFRS concepts in 20-F or 40-F filings.
    """
    facts = company_facts.get("facts", {})
    namespaces = ["us-gaap", "ifrs-full"]
    best_result = []

    for namespace in namespaces:
        namespace_facts = facts.get(namespace, {})
        for tag in candidates:
            fact = namespace_facts.get(tag)
            if not fact:
                continue
            result = _annual_value_records(fact)
            if len(result) > len(best_result):
                best_result = result

    return best_result


def get_fact(company_facts, fact_name):
    """Get an annual fact by exact tag, preserving SEC provenance."""
    return _get_fact_from_namespaces(company_facts, [fact_name])


def get_net_income(company_facts):
    return _get_fact_from_namespaces(
        company_facts,
        ["ProfitLoss", "NetIncomeLoss", "ProfitLossAttributableToOwnersOfParent"],
    )


def get_revenue(company_facts):
    return _get_fact_from_namespaces(
        company_facts,
        [
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "Revenue",
            "SalesRevenueNet",
            "Revenues",
        ],
    )


def get_cash(company_facts):
    return _get_fact_from_namespaces(
        company_facts,
        [
            "CashAndCashEquivalentsAtCarryingValue",
            "CashAndCashEquivalents",
            "CashCashEquivalentsAndShortTermInvestments",
        ],
    )


def get_receivables(company_facts):
    return _get_fact_from_namespaces(
        company_facts,
        [
            "AccountsReceivableNetCurrent",
            "TradeAndOtherCurrentReceivables",
            "TradeAndOtherReceivables",
            "AccountsReceivableCurrent",
        ],
    )


def get_inventory(company_facts):
    return _get_fact_from_namespaces(
        company_facts,
        [
            "InventoryNet",
            "Inventories",
            "InventoryFinishedGoods",
        ],
    )


def get_operating_cash_flow(company_facts):
    return _get_fact_from_namespaces(
        company_facts,
        [
            "NetCashProvidedByUsedInOperatingActivities",
            "CashFlowsFromUsedInOperatingActivities",
            "CashGeneratedFromUsedInOperations",
        ],
    )


def get_capex(company_facts):
    return _get_fact_from_namespaces(
        company_facts,
        [
            "PaymentsToAcquirePropertyPlantAndEquipment",
            "PurchaseOfPropertyPlantAndEquipment",
            "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities",
            "PaymentsToAcquirePropertyPlantAndEquipmentClassifiedAsInvestingActivities",
        ],
    )


def get_debt(company_facts):
    """Extract annual current and non-current debt without double counting."""
    current = _get_fact_from_namespaces(
        company_facts,
        [
            "LongTermDebtAndFinanceLeaseObligationsCurrent",
            "LongTermDebtCurrent",
            "BorrowingsCurrent",
            "CurrentBorrowings",
            "ShortTermBorrowings",
        ],
    )
    noncurrent = _get_fact_from_namespaces(
        company_facts,
        [
            "LongTermDebtAndFinanceLeaseObligationsNoncurrent",
            "LongTermDebtNoncurrent",
            "BorrowingsNoncurrent",
            "NoncurrentBorrowings",
        ],
    )

    yearly_results = {}
    for records, field in [(current, "current"), (noncurrent, "noncurrent")]:
        for value in records:
            year = value["year"]
            item = yearly_results.setdefault(
                year,
                {
                    "year": year,
                    "current": 0,
                    "noncurrent": 0,
                    "filed": value["filed"],
                    "end": value["end"],
                    "accn": value.get("accn"),
                    "form": value.get("form"),
                },
            )
            item[field] = value.get("value", 0) or 0
            if value["filed"] > item["filed"]:
                item.update(
                    filed=value["filed"],
                    end=value["end"],
                    accn=value.get("accn"),
                    form=value.get("form"),
                )

    for item in yearly_results.values():
        item["value"] = item["current"] + item["noncurrent"]

    return sorted(yearly_results.values(), key=lambda x: x["year"])


def get_goodwill(company_facts):
    """Extract only recent annual goodwill balances aligned with current assets."""
    goodwill = _get_fact_from_namespaces(company_facts, ["Goodwill"])
    assets = get_assets(company_facts)
    if not goodwill or not assets:
        return []

    latest_asset_year = assets[-1]["year"]
    return [
        item for item in goodwill
        if item["year"] in {latest_asset_year, latest_asset_year - 1}
    ]


def get_assets(company_facts):
    return _get_fact_from_namespaces(company_facts, ["Assets"])


def get_liabilities(company_facts):
    return _get_fact_from_namespaces(company_facts, ["Liabilities"])


def get_current_assets(company_facts):
    return _get_fact_from_namespaces(company_facts, ["AssetsCurrent", "CurrentAssets"])


def get_current_liabilities(company_facts):
    return _get_fact_from_namespaces(
        company_facts,
        ["LiabilitiesCurrent", "CurrentLiabilities"],
    )


def get_financial_data(company_facts):
    return {
        "revenue": get_revenue(company_facts),
        "net_income": get_net_income(company_facts),
        "assets": get_assets(company_facts),
        "cash": get_cash(company_facts),
        "liabilities": get_liabilities(company_facts),
        "debt": get_debt(company_facts),
        "receivables": get_receivables(company_facts),
        "inventory": get_inventory(company_facts),
        "goodwill": get_goodwill(company_facts),
        "operating_cash_flow": get_operating_cash_flow(company_facts),
        "capital_expenditures": get_capex(company_facts),
        "current_assets": get_current_assets(company_facts),
        "current_liabilities": get_current_liabilities(company_facts),
    }
