from data.ticker_map import get_cik_from_ticker
from data.xbrl import get_company_facts
from data.financial_data import get_financial_data

from analysis.financial_ratios import calculate_growth
from analysis.financial_ratios import calculate_cash_flow_conversion
from analysis.financial_ratios import calculate_fcf
from analysis.financial_ratios import calculate_fcf_conversion
from analysis.financial_ratios import calculate_dso

from analysis.risk_indicators import check_revenue_vs_receivables
from analysis.risk_indicators import check_cash_flow_conversion
from analysis.risk_indicators import check_inventory_vs_revenue
from analysis.risk_indicators import check_liabilities_vs_assets
from analysis.risk_indicators import check_dso_change
from analysis.risk_indicators import check_fcf_conversion
from analysis.risk_indicators import check_current_ratio
from analysis.risk_indicators import check_debt_growth


ticker = "AAPL"

cik = get_cik_from_ticker(ticker)
company_facts = get_company_facts(cik)
financial_data = get_financial_data(company_facts)


revenue = financial_data["revenue"]
receivables = financial_data["receivables"]
inventory = financial_data["inventory"]
liabilities = financial_data["liabilities"]
assets = financial_data["assets"]
debt = financial_data["debt"]
operating_cash_flow = financial_data["operating_cash_flow"]
capital_expenditures = financial_data["capital_expenditures"]
net_income = financial_data["net_income"]
current_assets = financial_data["current_assets"]
current_liabilities = financial_data["current_liabilities"]


revenue_growth = calculate_growth(
    revenue[-1]["value"],
    revenue[-2]["value"]
)

receivables_growth = calculate_growth(
    receivables[-1]["value"],
    receivables[-2]["value"]
)

inventory_growth = calculate_growth(
    inventory[-1]["value"],
    inventory[-2]["value"]
)

liabilities_growth = calculate_growth(
    liabilities[-1]["value"],
    liabilities[-2]["value"]
)

assets_growth = calculate_growth(
    assets[-1]["value"],
    assets[-2]["value"]
)

debt_growth = calculate_growth(
    debt[-1]["value"],
    debt[-2]["value"]
)

cash_flow_conversion = calculate_cash_flow_conversion(
    operating_cash_flow[-1]["value"],
    net_income[-1]["value"]
)

free_cash_flow = calculate_fcf(
    operating_cash_flow[-1]["value"],
    capital_expenditures[-1]["value"]
)

fcf_conversion = calculate_fcf_conversion(
    free_cash_flow,
    net_income[-1]["value"]
)

current_ratio = (
    current_assets[-1]["value"]
    / current_liabilities[-1]["value"]
)

current_dso = calculate_dso(
    receivables[-1]["value"],
    revenue[-1]["value"]
)

previous_dso = calculate_dso(
    receivables[-2]["value"],
    revenue[-2]["value"]
)

dso_change = calculate_growth(
    current_dso,
    previous_dso
)


print("APPLE RISK INDICATORS")
print("==============================")

print()
print("REVENUE VS RECEIVABLES")
print(check_revenue_vs_receivables(
    revenue_growth,
    receivables_growth
))

print()
print("CASH FLOW")
print(check_cash_flow_conversion(
    cash_flow_conversion
))

print()
print("INVENTORY VS REVENUE")
print(check_inventory_vs_revenue(
    inventory_growth,
    revenue_growth
))

print()
print("LIABILITIES VS ASSETS")
print(check_liabilities_vs_assets(
    liabilities_growth,
    assets_growth
))

print()
print("DSO")
print(check_dso_change(
    dso_change
))

print()
print("FREE CASH FLOW")
print(check_fcf_conversion(
    fcf_conversion
))

print()
print("CURRENT RATIO")
print(check_current_ratio(
    current_ratio
))

print()
print("DEBT")
print(check_debt_growth(
    debt_growth
))