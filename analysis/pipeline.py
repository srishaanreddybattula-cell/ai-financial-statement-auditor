from analysis.accruals import assess_accrual_quality
from analysis.accounting_policies import analyze_accounting_policies
from analysis.anomaly_detection import detect_growth_acceleration, detect_historical_growth_anomalies
from analysis.cash_flow import assess_cash_flow
from analysis.data_quality import assess_data_quality
from analysis.goodwill import assess_goodwill_risk
from analysis.risk_assessment import assess_policy_risk, assess_risk_dimensions
from analysis.risk_score import calculate_risk_score, get_risk_category
from analysis.working_capital import assess_working_capital
from data.financial_data import get_financial_data
from data.filings import (
    analyze_accounting_topic,
    extract_accounting_topics,
    extract_filing_text,
    extract_formatted_sections,
    get_filing_document,
)
from data.normalizer import normalize_annual_data


ANNUAL_FORMS = {"10-K", "20-F", "40-F"}


def _latest_two(data):
    normalized = normalize_annual_data(data)
    if len(normalized) < 2:
        return None, None
    return normalized[-1], normalized[-2]


def _matching_annual_periods(data, target_year):
    """Return only the target and immediately prior annual periods."""
    normalized = normalize_annual_data(data)
    by_year = {item["year"]: item for item in normalized}
    return by_year.get(target_year), by_year.get(target_year - 1)


def find_latest_annual_filing(submissions, cik=None):
    """Find the latest annual report filed with the SEC."""
    recent = submissions.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])

    for i, form in enumerate(forms):
        if form not in ANNUAL_FORMS:
            continue

        accession_number = recent["accessionNumber"][i]
        primary_document = recent["primaryDocument"][i]
        filing = {
            "form": form,
            "accession_number": accession_number,
            "primary_document": primary_document,
            "filing_date": recent["filingDate"][i],
            "report_date": recent["reportDate"][i],
        }

        if cik is not None:
            clean_accession = accession_number.replace("-", "")
            filing["sec_url"] = (
                f"https://www.sec.gov/Archives/edgar/data/"
                f"{int(str(cik).zfill(10))}/{clean_accession}/{primary_document}"
            )

        return filing

    return None


# Backward-compatible name used by existing tests/imports.
def find_latest_10k(submissions, cik=None):
    return find_latest_annual_filing(submissions, cik)


def analyze_company(cik, submissions, company_facts):
    financial_data = get_financial_data(company_facts)
    data_quality = assess_data_quality(financial_data)

    revenue = normalize_annual_data(financial_data["revenue"])
    net_income = normalize_annual_data(financial_data["net_income"])
    assets = normalize_annual_data(financial_data["assets"])
    liabilities = normalize_annual_data(financial_data["liabilities"])
    debt = normalize_annual_data(financial_data["debt"])
    receivables = normalize_annual_data(financial_data["receivables"])
    inventory = normalize_annual_data(financial_data["inventory"])
    operating_cash_flow = normalize_annual_data(financial_data["operating_cash_flow"])
    capital_expenditures = normalize_annual_data(financial_data["capital_expenditures"])
    current_assets = normalize_annual_data(financial_data["current_assets"])
    current_liabilities = normalize_annual_data(financial_data["current_liabilities"])
    goodwill = normalize_annual_data(financial_data["goodwill"])

    latest_revenue, previous_revenue = _latest_two(revenue)
    latest_net_income, previous_net_income = _latest_two(net_income)
    latest_assets, _ = _latest_two(assets)
    latest_liabilities, _ = _latest_two(liabilities)
    latest_debt, _ = _latest_two(debt)
    latest_receivables, previous_receivables = _latest_two(receivables)
    latest_inventory, previous_inventory = _latest_two(inventory)
    latest_ocf, previous_ocf = _latest_two(operating_cash_flow)
    latest_capex, previous_capex = _latest_two(capital_expenditures)
    latest_current_assets, _ = _latest_two(current_assets)
    latest_current_liabilities, _ = _latest_two(current_liabilities)

    if latest_revenue is None:
        raise ValueError("The SEC data does not contain a latest annual revenue fact.")

    latest_goodwill, previous_goodwill = _matching_annual_periods(goodwill, latest_revenue["year"])

    required = [
        latest_revenue,
        previous_revenue,
        latest_net_income,
        previous_net_income,
        latest_assets,
        latest_receivables,
        previous_receivables,
        latest_inventory,
        previous_inventory,
        latest_ocf,
        previous_ocf,
        latest_capex,
        previous_capex,
        latest_current_assets,
        latest_current_liabilities,
    ]

    if any(item is None for item in required):
        raise ValueError("The SEC data does not contain enough annual facts for the full analysis.")

    revenue_growth = ((latest_revenue["value"] - previous_revenue["value"]) / previous_revenue["value"]) * 100
    receivables_growth = ((latest_receivables["value"] - previous_receivables["value"]) / previous_receivables["value"]) * 100
    inventory_growth = ((latest_inventory["value"] - previous_inventory["value"]) / previous_inventory["value"]) * 100

    current_ratio = None
    if latest_current_liabilities["value"] not in (None, 0):
        current_ratio = latest_current_assets["value"] / latest_current_liabilities["value"]

    debt_to_assets = None
    if latest_debt is not None and latest_assets["value"] not in (None, 0):
        debt_to_assets = latest_debt["value"] / latest_assets["value"]

    liabilities_to_assets = None
    if latest_liabilities is not None and latest_assets["value"] not in (None, 0):
        liabilities_to_assets = latest_liabilities["value"] / latest_assets["value"]

    indicators = {
        "revenue_vs_receivables": {"flag": receivables_growth - revenue_growth >= 10},
        "dso": {"flag": False},
        "cash_flow": {"flag": False},
        "free_cash_flow": {"flag": False},
        "inventory_vs_revenue": {"flag": inventory_growth - revenue_growth >= 10},
        "current_ratio": {"flag": False, "value": current_ratio},
        "debt_to_assets": {"value": debt_to_assets},
        "liabilities_to_assets": {"value": liabilities_to_assets},
    }

    accrual_result = assess_accrual_quality(
        latest_net_income["value"], latest_ocf["value"], latest_assets["value"]
    )

    working_capital_result = assess_working_capital(
        latest_receivables["value"], previous_receivables["value"],
        latest_inventory["value"], previous_inventory["value"],
        latest_revenue["value"], previous_revenue["value"],
        latest_current_assets["value"], latest_current_liabilities["value"]
    )

    cash_flow_result = assess_cash_flow(
        latest_ocf["value"], previous_ocf["value"],
        latest_net_income["value"], previous_net_income["value"],
        latest_capex["value"], previous_capex["value"]
    )

    indicators["dso"]["flag"] = (working_capital_result["dso_change"] or 0) >= 10
    indicators["cash_flow"]["flag"] = (cash_flow_result["cash_flow_conversion"] or 0) < 80
    indicators["free_cash_flow"]["flag"] = (cash_flow_result["fcf_conversion"] or 0) < 70
    indicators["current_ratio"]["flag"] = current_ratio is not None and current_ratio < 1

    goodwill_result = assess_goodwill_risk(
        latest_goodwill["value"] if latest_goodwill else None,
        latest_assets["value"],
        previous_goodwill["value"] if previous_goodwill else None,
    )

    risk_dimensions = assess_risk_dimensions(indicators)
    risk_dimensions["accrual_quality"] = accrual_result["risk_score"]
    risk_dimensions["cash_flow_quality"] = cash_flow_result["risk_score"]

    historical_anomalies = detect_historical_growth_anomalies(revenue)
    growth_accelerations = detect_growth_acceleration(revenue)

    filing = find_latest_annual_filing(submissions, cik)
    policy_result = None
    topic_analysis = {}

    if filing:
        html = get_filing_document(cik, filing["accession_number"], filing["primary_document"])
        text = extract_filing_text(html)
        sections = extract_formatted_sections(html)
        critical_estimates = sections.get("critical_accounting_estimates", "")
        policy_result = analyze_accounting_policies(critical_estimates)
        topics = extract_accounting_topics(critical_estimates)
        topic_analysis = {
            topic: analyze_accounting_topic(topic_text)
            for topic, topic_text in topics.items()
        }
        risk_dimensions["accounting_policy_risk"] = assess_policy_risk(topic_analysis)

    score = calculate_risk_score(risk_dimensions)

    return {
        "financial_data": financial_data,
        "data_quality": data_quality,
        "latest_year": latest_revenue["year"],
        "revenue_growth": revenue_growth,
        "receivables_growth": receivables_growth,
        "inventory_growth": inventory_growth,
        "accruals": accrual_result,
        "working_capital": working_capital_result,
        "cash_flow": cash_flow_result,
        "goodwill_analysis": goodwill_result,
        "historical_anomalies": historical_anomalies,
        "growth_accelerations": growth_accelerations,
        "risk_dimensions": risk_dimensions,
        "risk_score": score,
        "risk_category": get_risk_category(score),
        "filing": filing,
        "policy_analysis": policy_result,
        "accounting_topics": topic_analysis,
    }
