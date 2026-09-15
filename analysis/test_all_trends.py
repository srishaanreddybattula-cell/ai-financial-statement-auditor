from data.ticker_map import get_cik_from_ticker
from data.xbrl import get_company_facts
from data.financial_data import get_financial_data
from analysis.trends import calculate_year_over_year
from analysis.trends import calculate_multi_year_trend


ticker = "AAPL"

cik = get_cik_from_ticker(ticker)
company_facts = get_company_facts(cik)
financial_data = get_financial_data(company_facts)


metrics = [
    "revenue",
    "net_income",
    "assets",
    "cash",
    "liabilities",
    "debt",
    "receivables",
    "inventory",
    "operating_cash_flow",
    "capital_expenditures"
]


for metric in metrics:
    data = financial_data.get(metric, [])

    print("\n" + metric.upper())
    print("==============================")

    if not data:
        print("No data available.")
        continue

    year_over_year = calculate_year_over_year(data)
    multi_year = calculate_multi_year_trend(data)

    print("Year-over-year:", year_over_year)
    print("Multi-year:", multi_year)