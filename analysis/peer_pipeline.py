from analysis.peer_comparison import calculate_peer_deviation
from analysis.risk_score import calculate_risk_score, get_risk_category
from data.peer_data import collect_peer_metrics
from data.ticker_map import find_company


def add_peer_analysis(result, ticker):
    """Add peer screening when filing-period inputs are available.

    Peer comparison is supplemental and must never prevent the main SEC analysis
    from rendering for a company with incomplete XBRL coverage.
    """
    working_capital = result.get("working_capital", {})
    cash_flow = result.get("cash_flow", {})
    financial_data = result.get("financial_data", {})
    comparison_year = result.get("data_period_year") or result.get("latest_year")

    def value_for_year(data, year):
        for item in data or []:
            if item.get("year") == year:
                return item.get("value")
        return None

    revenue_value = value_for_year(financial_data.get("revenue"), comparison_year)
    receivables_value = value_for_year(financial_data.get("receivables"), comparison_year)
    assets_value = value_for_year(financial_data.get("assets"), comparison_year)
    net_income_value = value_for_year(financial_data.get("net_income"), comparison_year)
    ocf_value = value_for_year(financial_data.get("operating_cash_flow"), comparison_year)
    current_ratio = working_capital.get("current_ratio")

    if any(value is None for value in [revenue_value, receivables_value, assets_value, net_income_value, ocf_value, current_ratio, comparison_year]) or revenue_value == 0 or assets_value == 0:
        result["peer_comparison"] = {
            "risk_score": 0,
            "comparison_year": comparison_year,
            "peers": [],
            "metrics": {},
            "message": "Peer comparison is unavailable because the selected filing-period data is incomplete.",
        }
        return result

    company_metrics = {
        "receivables_to_revenue": (receivables_value / revenue_value) * 100,
        "dso": (receivables_value / revenue_value) * 365,
        "accrual_ratio": (net_income_value - ocf_value) / assets_value,
        "current_ratio": current_ratio,
        "ocf_conversion": cash_flow.get("cash_flow_conversion"),
    }

    if not ticker:
        result["peer_comparison"] = {
            "risk_score": 0,
            "comparison_year": comparison_year,
            "peers": [],
            "metrics": {},
            "message": "Peer comparison is unavailable because this SEC filer has no ticker mapping.",
        }
        return result

    try:
        company = find_company(ticker)
        normalized_ticker = company.get("ticker") if company else ticker.upper().strip()
        peer_metrics = collect_peer_metrics(normalized_ticker, target_year=comparison_year)
        peer_comparison = calculate_peer_deviation(company_metrics, peer_metrics)
    except Exception as exc:
        result["peer_comparison"] = {
            "risk_score": 0,
            "comparison_year": comparison_year,
            "peers": [],
            "metrics": {},
            "message": f"Peer comparison is temporarily unavailable: {exc}",
        }
        return result

    peer_comparison["comparison_year"] = comparison_year
    peer_comparison["peers"] = [{"ticker": peer.get("ticker"), "year": peer.get("year")} for peer in peer_metrics if peer.get("ticker")]
    result["peer_comparison"] = peer_comparison
    result["risk_dimensions"]["peer_deviation"] = peer_comparison.get("risk_score")
    result["risk_score"] = calculate_risk_score(result["risk_dimensions"])
    result["risk_category"] = get_risk_category(result["risk_score"])
    return result
