from analysis.financial_ratios import calculate_dso, calculate_receivables_to_revenue
from data.financial_data import get_financial_data
from data.normalizer import normalize_annual_data
from data.ticker_map import get_cik_from_ticker
from data.xbrl import get_company_facts


PEER_GROUPS = {
    "AAPL": ["MSFT", "GOOGL", "AMZN", "META"],
    "MSFT": ["AAPL", "GOOGL", "AMZN", "ORCL"],
    "GOOGL": ["META", "MSFT", "AMZN", "AAPL"],
    "AMZN": ["WMT", "MSFT", "GOOGL", "META"],
    "META": ["GOOGL", "MSFT", "AMZN", "AAPL"],
    "ORCL": ["MSFT", "SAP", "IBM", "AMZN"],
    "WMT": ["COST", "TGT", "AMZN", "HD"],
}


def get_peer_tickers(ticker):
    ticker = ticker.upper().strip()
    return PEER_GROUPS.get(ticker, [])


def _latest(data):
    normalized = normalize_annual_data(data)
    if not normalized:
        return None
    return normalized[-1]


def _for_year(data, target_year):
    normalized = normalize_annual_data(data)
    if target_year is None:
        return normalized[-1] if normalized else None
    for item in normalized:
        if item.get("year") == target_year:
            return item
    return None


def extract_peer_metrics(company_facts, target_year=None):
    financial_data = get_financial_data(company_facts)

    revenue = _for_year(financial_data["revenue"], target_year)
    assets = _for_year(financial_data["assets"], target_year)
    receivables = _for_year(financial_data["receivables"], target_year)
    net_income = _for_year(financial_data["net_income"], target_year)
    operating_cash_flow = _for_year(financial_data["operating_cash_flow"], target_year)
    current_assets = _for_year(financial_data["current_assets"], target_year)
    current_liabilities = _for_year(financial_data["current_liabilities"], target_year)

    required = [
        revenue,
        assets,
        receivables,
        net_income,
        operating_cash_flow,
        current_assets,
        current_liabilities,
    ]

    if any(item is None for item in required):
        return None

    revenue_value = revenue["value"]
    assets_value = assets["value"]
    receivables_value = receivables["value"]
    net_income_value = net_income["value"]
    ocf_value = operating_cash_flow["value"]
    current_assets_value = current_assets["value"]
    current_liabilities_value = current_liabilities["value"]

    if revenue_value == 0 or assets_value == 0 or current_liabilities_value == 0:
        return None

    comparison_year = revenue.get("year")

    return {
        "year": comparison_year,
        "receivables_to_revenue": calculate_receivables_to_revenue(
            receivables_value, revenue_value
        ),
        "dso": calculate_dso(receivables_value, revenue_value),
        "accrual_ratio": (net_income_value - ocf_value) / assets_value,
        "current_ratio": current_assets_value / current_liabilities_value,
        "ocf_conversion": (ocf_value / net_income_value) * 100
        if net_income_value != 0
        else None,
    }


def collect_peer_metrics(ticker, target_year=None):
    peer_tickers = get_peer_tickers(ticker)
    peers = []

    for peer_ticker in peer_tickers:
        cik = get_cik_from_ticker(peer_ticker)
        if cik is None:
            continue

        try:
            company_facts = get_company_facts(cik)
            metrics = extract_peer_metrics(company_facts, target_year=target_year)
        except Exception:
            continue

        if metrics is not None:
            metrics["ticker"] = peer_ticker
            peers.append(metrics)

    return peers
