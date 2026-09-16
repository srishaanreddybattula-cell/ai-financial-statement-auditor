from analysis.peer_comparison import calculate_peer_deviation
from analysis.risk_score import calculate_risk_score, get_risk_category
from data.peer_data import collect_peer_metrics
from data.ticker_map import find_company


def add_peer_analysis(result, ticker):
    working_capital = result.get("working_capital", {})
    cash_flow = result.get("cash_flow", {})
    financial_data = result.get("financial_data", {})

    revenue = financial_data.get("revenue", [])
    receivables = financial_data.get("receivables", [])
    assets = financial_data.get("assets", [])
    net_income = financial_data.get("net_income", [])
    operating_cash_flow = financial_data.get("operating_cash_flow", [])

    def latest_value(data):
        if not data:
            return None
        return sorted(data, key=lambda item: item.get("year", 0))[-1].get("value")

    def latest_year(data):
        if not data:
            return None
        return sorted(data, key=lambda item: item.get("year", 0))[-1].get("year")

    comparison_year = latest_year(revenue)
    revenue_value = latest_value(revenue)
    receivables_value = latest_value(receivables)
    assets_value = latest_value(assets)
    net_income_value = latest_value(net_income)
    ocf_value = latest_value(operating_cash_flow)
    current_ratio = working_capital.get("current_ratio")

    if any(value is None for value in [
        revenue_value,
        receivables_value,
        assets_value,
        net_income_value,
        ocf_value,
        current_ratio,
        comparison_year,
    ]):
        return result

    company_metrics = {
        "receivables_to_revenue": (receivables_value / revenue_value) * 100,
        "dso": (receivables_value / revenue_value) * 365,
        "accrual_ratio": (net_income_value - ocf_value) / assets_value,
        "current_ratio": current_ratio,
        "ocf_conversion": cash_flow.get("cash_flow_conversion"),
    }

    company = find_company(ticker)
    normalized_ticker = company.get("ticker") if company else ticker.upper().strip()
    peer_metrics = collect_peer_metrics(normalized_ticker, target_year=comparison_year)
    peer_comparison = calculate_peer_deviation(company_metrics, peer_metrics)
    peer_comparison["comparison_year"] = comparison_year
    peer_comparison["peers"] = [
        {
            "ticker": peer.get("ticker"),
            "year": peer.get("year"),
        }
        for peer in peer_metrics
        if peer.get("ticker")
    ]

    result["peer_comparison"] = peer_comparison
    result["risk_dimensions"]["peer_deviation"] = peer_comparison["risk_score"]
    result["risk_score"] = calculate_risk_score(result["risk_dimensions"])
    result["risk_category"] = get_risk_category(result["risk_score"])

    return result
