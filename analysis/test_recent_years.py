from data.ticker_map import get_cik_from_ticker
from data.xbrl import get_company_facts
from data.financial_data import get_financial_data
from analysis.trends import get_recent_years


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
    "inventory",
    "operating_cash_flow",
    "capital_expenditures"
]


for metric in metrics:
    data = financial_data.get(metric, [])

    print("\n" + metric.upper())
    print("==============================")

    recent_data = get_recent_years(data, 7)

    for item in recent_data:
        print(item)