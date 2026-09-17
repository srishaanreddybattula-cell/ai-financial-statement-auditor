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


ANNUAL_FORMS = {"10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A"}


def _latest_two(data):
    normalized = normalize_annual_data(data)
    if len(normalized) < 2:
        return None, None
    return normalized[-1], normalized[-2]


def _by_year(data):
    return {item["year"]: item for item in normalize_annual_data(data)}


def _period_pair(data, target_year):
    by_year = _by_year(data)
    return by_year.get(target_year), by_year.get(target_year - 1)


def _filing_year(filing):
    if not filing:
        return None
    report_date = filing.get("report_date")
    if not report_date:
        return None
    try:
        return int(str(report_date)[:4])
    except (TypeError, ValueError):
        return None


def find_latest_annual_filing(submissions, cik=None):
    """Find the latest annual report filed with the SEC, including amendments."""
    recent = submissions.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    candidates = []

    for i, form in enumerate(forms):
        if form not in ANNUAL_FORMS:
            continue
        try:
            accession_number = recent["accessionNumber"][i]
            primary_document = recent["primaryDocument"][i]
            filing_date = recent["filingDate"][i]
            report_date = recent["reportDate"][i]
        except (KeyError, IndexError):
            continue

        filing = {
            "form": form,
            "accession_number": accession_number,
            "primary_document": primary_document,
            "filing_date": filing_date,
            "report_date": report_date,
        }
        if cik is not None:
            clean_accession = accession_number.replace("-", "")
            filing["sec_url"] = (
                f"https://www.sec.gov/Archives/edgar/data/"
                f"{int(str(cik).zfill(10))}/{clean_accession}/{primary_document}"
            )
        candidates.append(filing)

    if not candidates:
        return None

    # SEC submission history is normally newest-first, but do not depend on
    # array order. Prefer the latest fiscal period, then the latest filing date,
    # and finally an amendment when all dates are otherwise equal.
    def sort_key(filing):
        report_date = str(filing.get("report_date") or "")
        filing_date = str(filing.get("filing_date") or "")
        is_amendment = filing.get("form", "").endswith("/A")
        return (report_date, filing_date, is_amendment)

    return max(candidates, key=sort_key)


# Backward-compatible name used by existing tests/imports.
def find_latest_10k(submissions, cik=None):
    return find_latest_annual_filing(submissions, cik)


def _percentage_change(current, previous):
    if current is None or previous in (None, 0):
        return None
    return ((current - previous) / abs(previous)) * 100


def _empty_working_capital():
    return {
        "dso": None,
        "previous_dso": None,
        "dso_change": None,
        "receivables_to_revenue": None,
        "receivables_growth": None,
        "inventory_turnover": None,
        "days_inventory": None,
        "inventory_to_revenue": None,
        "inventory_growth": None,
        "revenue_growth": None,
        "current_ratio": None,
        "quick_ratio": None,
        "risk_score": 0,
    }


def _empty_cash_flow():
    return {
        "cash_flow_conversion": None,
        "previous_cash_flow_conversion": None,
        "conversion_change": None,
        "free_cash_flow": None,
        "previous_free_cash_flow": None,
        "fcf_conversion": None,
        "operating_cash_flow_growth": None,
        "net_income_growth": None,
        "capital_expenditures_growth": None,
        "fcf_growth": None,
        "risk_score": 0,
    }


def _empty_accruals():
    return {"accrual_ratio": None, "earnings_cash_difference": None, "risk_score": 0}


def analyze_company(cik, submissions, company_facts):
    """Run the screening model without requiring every SEC metric to exist.

    The latest annual filing is selected first. Its report year is the dashboard's
    annual-period label, and every metric is requested for that same fiscal year.
    Missing metrics remain unavailable instead of aborting the entire analysis.
    """
    filing = find_latest_annual_filing(submissions, cik)
    filing_year = _filing_year(filing)
    financial_data = get_financial_data(company_facts)
    data_quality = assess_data_quality(financial_data)

    revenue = normalize_annual_data(financial_data.get("revenue", []))
    net_income = normalize_annual_data(financial_data.get("net_income", []))
    assets = normalize_annual_data(financial_data.get("assets", []))
    liabilities = normalize_annual_data(financial_data.get("liabilities", []))
    debt = normalize_annual_data(financial_data.get("debt", []))
    receivables = normalize_annual_data(financial_data.get("receivables", []))
    inventory = normalize_annual_data(financial_data.get("inventory", []))
    operating_cash_flow = normalize_annual_data(financial_data.get("operating_cash_flow", []))
    capital_expenditures = normalize_annual_data(financial_data.get("capital_expenditures", []))
    current_assets = normalize_annual_data(financial_data.get("current_assets", []))
    current_liabilities = normalize_annual_data(financial_data.get("current_liabilities", []))
    goodwill = normalize_annual_data(financial_data.get("goodwill", []))

    latest_data_year = revenue[-1]["year"] if revenue else filing_year
    analysis_year = filing_year if filing_year is not None else latest_data_year
    previous_year = analysis_year - 1 if analysis_year is not None else None

    latest_revenue, previous_revenue = _period_pair(revenue, analysis_year) if analysis_year else (None, None)
    latest_net_income, previous_net_income = _period_pair(net_income, analysis_year) if analysis_year else (None, None)
    latest_assets, _ = _period_pair(assets, analysis_year) if analysis_year else (None, None)
    latest_liabilities, _ = _period_pair(liabilities, analysis_year) if analysis_year else (None, None)
    latest_debt, _ = _period_pair(debt, analysis_year) if analysis_year else (None, None)
    latest_receivables, previous_receivables = _period_pair(receivables, analysis_year) if analysis_year else (None, None)
    latest_inventory, previous_inventory = _period_pair(inventory, analysis_year) if analysis_year else (None, None)
    latest_ocf, previous_ocf = _period_pair(operating_cash_flow, analysis_year) if analysis_year else (None, None)
    latest_capex, previous_capex = _period_pair(capital_expenditures, analysis_year) if analysis_year else (None, None)
    latest_current_assets, _ = _period_pair(current_assets, analysis_year) if analysis_year else (None, None)
    latest_current_liabilities, _ = _period_pair(current_liabilities, analysis_year) if analysis_year else (None, None)
    latest_goodwill, previous_goodwill = _period_pair(goodwill, analysis_year) if analysis_year else (None, None)

    warnings = []
    if filing is None:
        warnings.append("No recent annual SEC filing was found in the submission history.")
    if filing_year is not None and not latest_revenue:
        warnings.append(f"Revenue data for the filing period {filing_year} was not available in SEC XBRL; revenue-dependent metrics are shown as N/A.")

    revenue_growth = _percentage_change(
        latest_revenue.get("value") if latest_revenue else None,
        previous_revenue.get("value") if previous_revenue else None,
    )
    receivables_growth = _percentage_change(
        latest_receivables.get("value") if latest_receivables else None,
        previous_receivables.get("value") if previous_receivables else None,
    )
    inventory_growth = _percentage_change(
        latest_inventory.get("value") if latest_inventory else None,
        previous_inventory.get("value") if previous_inventory else None,
    )

    if all([
        latest_receivables,
        previous_receivables,
        latest_inventory,
        previous_inventory,
        latest_revenue,
        previous_revenue,
        latest_current_assets,
        latest_current_liabilities,
    ]):
        working_capital_result = assess_working_capital(
            latest_receivables["value"], previous_receivables["value"],
            latest_inventory["value"], previous_inventory["value"],
            latest_revenue["value"], previous_revenue["value"],
            latest_current_assets["value"], latest_current_liabilities["value"],
        )
    else:
        working_capital_result = _empty_working_capital()
        warnings.append("Working-capital analysis is partially unavailable because the required annual facts are incomplete.")

    if all([latest_net_income, previous_net_income, latest_ocf, previous_ocf, latest_capex, previous_capex]):
        cash_flow_result = assess_cash_flow(
            latest_ocf["value"], previous_ocf["value"],
            latest_net_income["value"], previous_net_income["value"],
            latest_capex["value"], previous_capex["value"],
        )
    else:
        cash_flow_result = _empty_cash_flow()
        warnings.append("Cash-flow analysis is partially unavailable because the required annual facts are incomplete.")

    if all([latest_net_income, latest_ocf, latest_assets]):
        accrual_result = assess_accrual_quality(
            latest_net_income["value"], latest_ocf["value"], latest_assets["value"]
        )
    else:
        accrual_result = _empty_accruals()
        warnings.append("Accrual analysis is unavailable because net income, operating cash flow, or assets are missing for the filing period.")

    debt_to_assets = None
    liabilities_to_assets = None
    if latest_assets and latest_assets["value"] not in (None, 0):
        if latest_debt:
            debt_to_assets = latest_debt["value"] / latest_assets["value"]
        if latest_liabilities:
            liabilities_to_assets = latest_liabilities["value"] / latest_assets["value"]

    current_ratio = working_capital_result.get("current_ratio")
    indicators = {
        "revenue_vs_receivables": {"flag": receivables_growth is not None and revenue_growth is not None and receivables_growth - revenue_growth >= 10},
        "dso": {"flag": working_capital_result.get("dso_change") is not None and working_capital_result["dso_change"] >= 10},
        "cash_flow": {"flag": cash_flow_result.get("cash_flow_conversion") is not None and cash_flow_result["cash_flow_conversion"] < 80},
        "free_cash_flow": {"flag": cash_flow_result.get("fcf_conversion") is not None and cash_flow_result["fcf_conversion"] < 70},
        "inventory_vs_revenue": {"flag": inventory_growth is not None and revenue_growth is not None and inventory_growth - revenue_growth >= 10},
        "current_ratio": {"flag": current_ratio is not None and current_ratio < 1, "value": current_ratio},
        "debt_to_assets": {"value": debt_to_assets},
        "liabilities_to_assets": {"value": liabilities_to_assets},
    }

    goodwill_result = assess_goodwill_risk(
        latest_goodwill["value"] if latest_goodwill else None,
        latest_assets["value"] if latest_assets else None,
        previous_goodwill["value"] if previous_goodwill else None,
    )

    risk_dimensions = assess_risk_dimensions(indicators)
    risk_dimensions["accrual_quality"] = accrual_result["risk_score"] if latest_net_income and latest_ocf and latest_assets else None
    risk_dimensions["cash_flow_quality"] = cash_flow_result["risk_score"] if latest_net_income and latest_ocf and latest_capex else None

    historical_anomalies = detect_historical_growth_anomalies(revenue) if len(revenue) >= 3 else []
    growth_accelerations = detect_growth_acceleration(revenue) if len(revenue) >= 2 else []

    policy_result = None
    topic_analysis = {}
    if filing:
        try:
            html = get_filing_document(cik, filing["accession_number"], filing["primary_document"])
            text = extract_filing_text(html)
            sections = extract_formatted_sections(html)
            critical_estimates = sections.get("critical_accounting_estimates", "")
            policy_result = analyze_accounting_policies(critical_estimates)
            topics = extract_accounting_topics(critical_estimates)
            topic_analysis = {topic: analyze_accounting_topic(topic_text) for topic, topic_text in topics.items()}
            risk_dimensions["accounting_policy_risk"] = assess_policy_risk(topic_analysis)
        except Exception as exc:
            warnings.append(f"Annual filing text could not be processed for policy review: {exc}")
            risk_dimensions["accounting_policy_risk"] = None

    score = calculate_risk_score(risk_dimensions)

    return {
        "financial_data": financial_data,
        "data_quality": data_quality,
        # This is deliberately tied to the selected annual filing, not whichever
        # XBRL concept happened to have the newest historical observation.
        "latest_year": analysis_year,
        "data_period_year": analysis_year,
        "filing_year": filing_year,
        "previous_year": previous_year,
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
        "analysis_warnings": list(dict.fromkeys(warnings)),
        "partial_analysis": bool(warnings),
    }
