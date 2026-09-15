from data.ticker_map import get_cik_from_ticker
from data.xbrl import get_company_facts
from data.financial_data import get_financial_data
from analysis.trends import calculate_year_over_year
from analysis.trends import calculate_multi_year_trend


ticker = "AAPL"

cik = get_cik_from_ticker(ticker)
company_facts = get_company_facts(cik)
financial_data = get_financial_data(company_facts)


revenue = financial_data["revenue"]


year_over_year = calculate_year_over_year(revenue)
multi_year = calculate_multi_year_trend(revenue)


print("APPLE REVENUE TRENDS")
print("==============================")

print("\nYEAR-OVER-YEAR")
print(year_over_year)

print("\nMULTI-YEAR TREND")
print(multi_year)