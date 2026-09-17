from datetime import date

ANNUAL_FORMS = {"10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A"}


def _fact_metadata(value):
    return {
        "form": value.get("form"),
        "accn": value.get("accn"),
        "accession_number": value.get("accn"),
        "frame": value.get("frame"),
    }


def _annual_value_records(fact):
    """Convert one SEC Company Facts concept into annual observations."""
    yearly_values = {}
    for values in fact.get("units", {}).values():
        for value in values:
            if value.get("form") not in ANNUAL_FORMS:
                continue
            end = value.get("end")
            filed = value.get("filed")
            if not end or not filed or value.get("val") is None:
                continue
            start = value.get("start")
            if start:
                try:
                    days = (date.fromisoformat(end) - date.fromisoformat(start)).days
                except ValueError:
                    continue
                if not 350 <= days <= 380:
                    continue
            try:
                year = int(end[:4])
            except (TypeError, ValueError):
                continue
            record = {
                "year": year,
                "value": value["val"],
                "filed": filed,
                "start": start,
                "end": end,
                **_fact_metadata(value),
            }
            if year not in yearly_values or filed > yearly_values[year]["filed"]:
                yearly_values[year] = record
    return sorted(yearly_values.values(), key=lambda item: item["year"])


def _get_fact_from_namespaces(company_facts, candidates):
    """Choose the most current usable annual concept across SEC taxonomies."""
    facts = company_facts.get("facts", {})
    preferred = ["us-gaap", "ifrs-full"]
    options = []
    for namespace_index, namespace in enumerate(preferred):
        for candidate_index, tag in enumerate(candidates):
            fact = facts.get(namespace, {}).get(tag)
            if fact:
                options.append((namespace_index, candidate_index, fact))
    for namespace, namespace_facts in facts.items():
        if namespace in preferred:
            continue
        for candidate_index, tag in enumerate(candidates):
            fact = namespace_facts.get(tag)
            if fact:
                options.append((2, candidate_index, fact))

    best_result = []
    best_key = None
    for namespace_index, candidate_index, fact in options:
        result = _annual_value_records(fact)
        if not result:
            continue
        key = (result[-1]["year"], len(result), -namespace_index, -candidate_index)
        if best_key is None or key > best_key:
            best_result = result
            best_key = key
    return best_result


def _keyword_fallback(company_facts, keyword_groups, exclude=None):
    """Find a current annual custom-taxonomy fact using semantic labels."""
    exclude = {word.lower() for word in (exclude or [])}
    candidates = []
    for namespace, namespace_facts in company_facts.get("facts", {}).items():
        for tag, fact in namespace_facts.items():
            haystack = f"{namespace} {tag} {fact.get('label', '')} {fact.get('description', '')}".lower()
            if any(word in haystack for word in exclude):
                continue
            if not all(any(word in haystack for word in group) for group in keyword_groups):
                continue
            records = _annual_value_records(fact)
            if not records:
                continue
            standard_bonus = 1 if namespace in {"us-gaap", "ifrs-full"} else 0
            candidates.append((records[-1]["year"], standard_bonus, len(records), records))
    if not candidates:
        return []
    candidates.sort(key=lambda item: item[:3], reverse=True)
    return candidates[0][3]


def _get_with_fallback(company_facts, candidates, keyword_groups=None, exclude=None):
    result = _get_fact_from_namespaces(company_facts, candidates)
    if result:
        return result
    return _keyword_fallback(company_facts, keyword_groups, exclude) if keyword_groups else []


def get_fact(company_facts, fact_name):
    return _get_fact_from_namespaces(company_facts, [fact_name])


def get_net_income(company_facts):
    return _get_with_fallback(company_facts, ["ProfitLoss", "NetIncomeLoss", "ProfitLossAttributableToOwnersOfParent"], [["net income", "net profit", "profit loss", "profit"]], ["operating profit", "gross profit", "revenue"])


def get_revenue(company_facts):
    return _get_with_fallback(company_facts, ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenue", "SalesRevenueNet", "Revenues"], [["revenue", "sales", "turnover"]], ["cost", "expense", "growth rate"])


def get_cash(company_facts):
    return _get_with_fallback(company_facts, ["CashAndCashEquivalentsAtCarryingValue", "CashAndCashEquivalents", "CashCashEquivalentsAndShortTermInvestments"], [["cash"], ["equivalent", "short-term investment", "short term investment"]], ["flow", "payment", "proceeds"])


def get_receivables(company_facts):
    return _get_with_fallback(company_facts, ["AccountsReceivableNetCurrent", "TradeAndOtherCurrentReceivables", "TradeAndOtherReceivables", "AccountsReceivableCurrent"], [["receivable"]], ["allowance", "provision"])


def get_inventory(company_facts):
    return _get_with_fallback(company_facts, ["InventoryNet", "Inventories", "InventoryFinishedGoods"], [["inventory", "inventories"]], ["turnover", "days"])


def get_operating_cash_flow(company_facts):
    return _get_with_fallback(company_facts, ["NetCashProvidedByUsedInOperatingActivities", "CashFlowsFromUsedInOperatingActivities", "CashGeneratedFromUsedInOperations"], [["operating"], ["cash"]], ["revenue", "expense", "income"])


def get_capex(company_facts):
    return _get_with_fallback(company_facts, ["PaymentsToAcquirePropertyPlantAndEquipment", "PurchaseOfPropertyPlantAndEquipment", "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities", "PaymentsToAcquirePropertyPlantAndEquipmentClassifiedAsInvestingActivities"], [["property", "plant and equipment", "ppe"], ["acquire", "purchase", "capital expenditure"]])


def get_debt(company_facts):
    current = _get_with_fallback(company_facts, ["LongTermDebtAndFinanceLeaseObligationsCurrent", "LongTermDebtCurrent", "BorrowingsCurrent", "CurrentBorrowings", "ShortTermBorrowings"], [["current"], ["debt", "borrowings", "borrowing"]], ["asset", "receivable"])
    noncurrent = _get_with_fallback(company_facts, ["LongTermDebtAndFinanceLeaseObligationsNoncurrent", "LongTermDebtNoncurrent", "BorrowingsNoncurrent", "NoncurrentBorrowings"], [["noncurrent", "non-current", "long-term"], ["debt", "borrowings", "borrowing"]], ["asset", "receivable"])
    yearly_results = {}
    for records, field in [(current, "current"), (noncurrent, "noncurrent")]:
        for value in records:
            year = value["year"]
            item = yearly_results.setdefault(year, {"year": year, "current": 0, "noncurrent": 0, "filed": value["filed"], "end": value["end"], "accn": value.get("accn"), "form": value.get("form")})
            item[field] = value.get("value", 0) or 0
            if value["filed"] > item["filed"]:
                item.update(filed=value["filed"], end=value["end"], accn=value.get("accn"), form=value.get("form"))
    for item in yearly_results.values():
        item["value"] = item["current"] + item["noncurrent"]
    return sorted(yearly_results.values(), key=lambda item: item["year"])


def get_assets(company_facts):
    return _get_with_fallback(company_facts, ["Assets"], [["assets"]], ["asset turnover"])


def get_liabilities(company_facts):
    return _get_with_fallback(company_facts, ["Liabilities"], [["liabilities", "liability"]], ["asset"])


def get_current_assets(company_facts):
    return _get_with_fallback(company_facts, ["AssetsCurrent", "CurrentAssets"], [["current"], ["assets"]])


def get_current_liabilities(company_facts):
    return _get_with_fallback(company_facts, ["LiabilitiesCurrent", "CurrentLiabilities"], [["current"], ["liabilit"]])


def get_goodwill(company_facts):
    goodwill = _get_with_fallback(company_facts, ["Goodwill"], [["goodwill"]])
    assets = get_assets(company_facts)
    if not goodwill or not assets:
        return []
    latest_asset_year = assets[-1]["year"]
    return [item for item in goodwill if item["year"] in {latest_asset_year, latest_asset_year - 1}]


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
