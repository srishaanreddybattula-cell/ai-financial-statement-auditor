from data.ticker_map import get_cik_from_ticker
from data.xbrl import get_company_facts
from data.financial_data import get_financial_data


ticker = "AAPL"

cik = get_cik_from_ticker(ticker)
company_facts = get_company_facts(cik)
financial_data = get_financial_data(company_facts)

receivables = financial_data["receivables"]

print("APPLE RECEIVABLES")
print("==============================")

for item in receivables:
    print(item)