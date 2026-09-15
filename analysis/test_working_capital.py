from data.ticker_map import get_cik_from_ticker
from data.xbrl import get_company_facts
from data.financial_data import get_financial_data

from analysis.working_capital import assess_working_capital


ticker = "AAPL"

cik = get_cik_from_ticker(ticker)
company_facts = get_company_facts(cik)
financial_data = get_financial_data(company_facts)

receivables = financial_data["receivables"][-1]["value"]
previous_receivables = financial_data["receivables"][-2]["value"]

inventory = financial_data["inventory"][-1]["value"]
previous_inventory = financial_data["inventory"][-2]["value"]

revenue = financial_data["revenue"][-1]["value"]
previous_revenue = financial_data["revenue"][-2]["value"]

current_assets = financial_data["current_assets"][-1]["value"]
current_liabilities = financial_data["current_liabilities"][-1]["value"]


result = assess_working_capital(
    receivables,
    previous_receivables,
    inventory,
    previous_inventory,
    revenue,
    previous_revenue,
    current_assets,
    current_liabilities
)


print("APPLE WORKING CAPITAL ANALYSIS")
print("==============================")

print(f"DSO: {result['dso']:.2f} days")
print(f"Previous DSO: {result['previous_dso']:.2f} days")
print(f"DSO change: {result['dso_change']:.2f}%")

print(
    f"Receivables / Revenue: "
    f"{result['receivables_to_revenue']:.2f}%"
)

print(
    f"Receivables growth: "
    f"{result['receivables_growth']:.2f}%"
)

print(
    f"Inventory turnover: "
    f"{result['inventory_turnover']:.2f}x"
)

print(
    f"Days inventory: "
    f"{result['days_inventory']:.2f} days"
)

print(
    f"Inventory / Revenue: "
    f"{result['inventory_to_revenue']:.2f}%"
)

print(
    f"Inventory growth: "
    f"{result['inventory_growth']:.2f}%"
)

print(
    f"Revenue growth: "
    f"{result['revenue_growth']:.2f}%"
)

print(f"Current ratio: {result['current_ratio']:.2f}")
print(f"Quick ratio: {result['quick_ratio']:.2f}")

print()
print(
    f"Working capital risk score: "
    f"{result['risk_score']}/100"
)