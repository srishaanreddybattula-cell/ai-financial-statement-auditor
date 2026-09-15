from data.ticker_map import get_cik_from_ticker
from data.xbrl import get_company_facts
from data.financial_data import get_financial_data

from analysis.cash_flow import assess_cash_flow


ticker = "AAPL"

cik = get_cik_from_ticker(ticker)
company_facts = get_company_facts(cik)
financial_data = get_financial_data(company_facts)

operating_cash_flow = financial_data["operating_cash_flow"][-1]["value"]
previous_operating_cash_flow = financial_data["operating_cash_flow"][-2]["value"]

net_income = financial_data["net_income"][-1]["value"]
previous_net_income = financial_data["net_income"][-2]["value"]

capital_expenditures = financial_data["capital_expenditures"][-1]["value"]
previous_capital_expenditures = financial_data["capital_expenditures"][-2]["value"]


result = assess_cash_flow(
    operating_cash_flow,
    previous_operating_cash_flow,
    net_income,
    previous_net_income,
    capital_expenditures,
    previous_capital_expenditures
)


print("APPLE CASH FLOW ANALYSIS")
print("==============================")

print(
    f"Operating cash flow conversion: "
    f"{result['cash_flow_conversion']:.2f}%"
)

print(
    f"Previous OCF conversion: "
    f"{result['previous_cash_flow_conversion']:.2f}%"
)

print(
    f"Conversion change: "
    f"{result['conversion_change']:.2f} percentage points"
)

print(
    f"Free cash flow: "
    f"${result['free_cash_flow'] / 1_000_000_000:.2f}B"
)

print(
    f"Previous free cash flow: "
    f"${result['previous_free_cash_flow'] / 1_000_000_000:.2f}B"
)

print(
    f"FCF conversion: "
    f"{result['fcf_conversion']:.2f}%"
)

print(
    f"Operating cash flow growth: "
    f"{result['operating_cash_flow_growth']:.2f}%"
)

print(
    f"Net income growth: "
    f"{result['net_income_growth']:.2f}%"
)

print(
    f"Capital expenditures growth: "
    f"{result['capital_expenditures_growth']:.2f}%"
)

print(
    f"Free cash flow growth: "
    f"{result['fcf_growth']:.2f}%"
)

print()
print(
    f"Cash flow risk score: "
    f"{result['risk_score']}/100"
)