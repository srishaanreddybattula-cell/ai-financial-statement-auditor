from data.ticker_map import get_cik_from_ticker
from data.xbrl import get_company_facts
from data.financial_data import get_financial_data

from analysis.financial_ratios import calculate_growth
from analysis.financial_ratios import calculate_profit_margin
from analysis.financial_ratios import calculate_cash_flow_conversion
from analysis.financial_ratios import calculate_fcf
from analysis.financial_ratios import calculate_fcf_conversion
from analysis.financial_ratios import calculate_current_ratio
from analysis.financial_ratios import calculate_receivables_to_revenue
from analysis.financial_ratios import calculate_dso


ticker = "AAPL"

cik = get_cik_from_ticker(ticker)
company_facts = get_company_facts(cik)
financial_data = get_financial_data(company_facts)


revenue = financial_data["revenue"]
net_income = financial_data["net_income"]
operating_cash_flow = financial_data["operating_cash_flow"]
capital_expenditures = financial_data["capital_expenditures"]
receivables = financial_data["receivables"]
current_assets = financial_data["current_assets"]
current_liabilities = financial_data["current_liabilities"]


current_revenue = revenue[-1]["value"]
previous_revenue = revenue[-2]["value"]

current_net_income = net_income[-1]["value"]
current_ocf = operating_cash_flow[-1]["value"]
current_capex = capital_expenditures[-1]["value"]
current_receivables = receivables[-1]["value"]
current_current_assets = current_assets[-1]["value"]
current_current_liabilities = current_liabilities[-1]["value"]


revenue_growth = calculate_growth(
    current_revenue,
    previous_revenue
)

profit_margin = calculate_profit_margin(
    current_net_income,
    current_revenue
)

cash_flow_conversion = calculate_cash_flow_conversion(
    current_ocf,
    current_net_income
)

free_cash_flow = calculate_fcf(
    current_ocf,
    current_capex
)

fcf_conversion = calculate_fcf_conversion(
    free_cash_flow,
    current_net_income
)

current_ratio = calculate_current_ratio(
    current_current_assets,
    current_current_liabilities
)

receivables_to_revenue = calculate_receivables_to_revenue(
    current_receivables,
    current_revenue
)

dso = calculate_dso(
    current_receivables,
    current_revenue
)


print("APPLE FINANCIAL RATIOS")
print("==============================")

print(f"Revenue growth: {revenue_growth:.2f}%")
print(f"Profit margin: {profit_margin:.2f}%")
print(f"Cash flow conversion: {cash_flow_conversion:.2f}%")
print(f"Free cash flow: ${free_cash_flow / 1_000_000_000:.2f}B")
print(f"FCF conversion: {fcf_conversion:.2f}%")
print(f"Current ratio: {current_ratio:.2f}")
print(f"Receivables / revenue: {receivables_to_revenue:.2f}%")
print(f"DSO: {dso:.2f} days")