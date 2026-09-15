import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xbrl import get_company_facts
from financial_data import get_financial_data
from normalizer import normalize_annual_data

from analysis.financial_ratios import (
    calculate_growth,
    calculate_profit_margin,
    calculate_receivables_to_revenue,
    calculate_cash_flow_conversion,
    calculate_dso,
    calculate_fcf_conversion,
    calculate_current_ratio,
    calculate_trend
)

from analysis.risk_indicators import (
    check_revenue_vs_receivables,
    check_cash_flow_conversion,
    check_inventory_vs_revenue,
    check_liabilities_vs_assets,
    check_dso_change,
    check_fcf_conversion,
    check_current_ratio,
    check_debt_growth
)

from analysis.risk_score import (
    calculate_risk_score,
    get_risk_category
)

from analysis.anomaly_detection import (
    detect_growth_anomalies,
    detect_receivables_anomalies
)


company_facts = get_company_facts("320193")

financial_data = get_financial_data(company_facts)

for key in financial_data:
    financial_data[key] = normalize_annual_data(financial_data[key])


revenue = financial_data["revenue"]
net_income = financial_data["net_income"]
assets = financial_data["assets"]
liabilities = financial_data["liabilities"]
receivables = financial_data["accounts_receivable"]
inventory = financial_data["inventory"]
operating_cash_flow = financial_data["operating_cash_flow"]
capital_expenditures = financial_data["capital_expenditures"]
debt = financial_data["debt"]
current_assets = financial_data["current_assets"]
current_liabilities = financial_data["current_liabilities"]


latest_revenue = revenue[-1]["value"]
previous_revenue = revenue[-2]["value"]

latest_net_income = net_income[-1]["value"]

latest_assets = assets[-1]["value"]
previous_assets = assets[-2]["value"]

latest_liabilities = liabilities[-1]["value"]
previous_liabilities = liabilities[-2]["value"]

latest_receivables = receivables[-1]["value"]
previous_receivables = receivables[-2]["value"]

latest_inventory = inventory[-1]["value"]
previous_inventory = inventory[-2]["value"]

latest_operating_cash_flow = operating_cash_flow[-1]["value"]

latest_capex = capital_expenditures[-1]["value"]

latest_current_assets = current_assets[-1]["value"]
latest_current_liabilities = current_liabilities[-1]["value"]


revenue_growth = calculate_growth(
    latest_revenue,
    previous_revenue
)

receivables_growth = calculate_growth(
    latest_receivables,
    previous_receivables
)

inventory_growth = calculate_growth(
    latest_inventory,
    previous_inventory
)

assets_growth = calculate_growth(
    latest_assets,
    previous_assets
)

liabilities_growth = calculate_growth(
    latest_liabilities,
    previous_liabilities
)

debt_growth = calculate_growth(
    debt[-1]["value"],
    debt[-2]["value"]
)


profit_margin = calculate_profit_margin(
    latest_net_income,
    latest_revenue
)

receivables_to_revenue = calculate_receivables_to_revenue(
    latest_receivables,
    latest_revenue
)

cash_flow_conversion = calculate_cash_flow_conversion(
    latest_operating_cash_flow,
    latest_net_income
)

dso = calculate_dso(
    latest_receivables,
    latest_revenue
)

previous_dso = calculate_dso(
    previous_receivables,
    previous_revenue
)

dso_change = calculate_growth(
    dso,
    previous_dso
)


free_cash_flow = latest_operating_cash_flow - latest_capex

fcf_conversion = calculate_fcf_conversion(
    free_cash_flow,
    latest_net_income
)

current_ratio = calculate_current_ratio(
    latest_current_assets,
    latest_current_liabilities
)


revenue_trend = calculate_trend(revenue)

revenue_anomalies = detect_growth_anomalies(
    revenue_trend
)

receivables_anomaly = detect_receivables_anomalies(
    revenue_growth,
    receivables_growth
)


revenue_receivables_risk = check_revenue_vs_receivables(
    revenue_growth,
    receivables_growth
)

cash_flow_risk = check_cash_flow_conversion(
    cash_flow_conversion
)

inventory_risk = check_inventory_vs_revenue(
    inventory_growth,
    revenue_growth
)

liabilities_assets_risk = check_liabilities_vs_assets(
    liabilities_growth,
    assets_growth
)

dso_risk = check_dso_change(
    dso_change
)

fcf_risk = check_fcf_conversion(
    fcf_conversion
)

current_ratio_risk = check_current_ratio(
    current_ratio
)

debt_risk = check_debt_growth(
    debt_growth
)


score = calculate_risk_score(
    revenue_receivables_risk["flag"],
    cash_flow_risk["flag"],
    inventory_risk["flag"],
    liabilities_assets_risk["flag"],
    dso_risk["flag"],
    fcf_risk["flag"],
    current_ratio_risk["flag"],
    debt_risk["flag"]
)

category = get_risk_category(score)


print()
print("FINANCIAL RISK ANALYSIS")
print("==============================")

print(f"Revenue Growth: {revenue_growth:.2f}%")
print("Revenue Trend:", revenue_trend)
print("Revenue Anomalies:", revenue_anomalies)

print("Receivables Anomaly:", receivables_anomaly)

print(f"DSO: {dso:.2f} days")
print(f"Previous DSO: {previous_dso:.2f} days")
print(f"DSO Change: {dso_change:.2f}%")

print(f"Inventory Growth: {inventory_growth:.2f}%")
print(f"Assets Growth: {assets_growth:.2f}%")
print(f"Liabilities Growth: {liabilities_growth:.2f}%")
print(f"Debt Growth: {debt_growth:.2f}%")

print(f"Cash Flow Conversion: {cash_flow_conversion:.2f}%")

print("Capital Expenditures:", capital_expenditures)

print(f"Free Cash Flow: {free_cash_flow}")
print(f"FCF Conversion: {fcf_conversion:.2f}%")

print(f"Current Ratio: {current_ratio:.2f}")

print("Debt:", debt)


print()

if revenue_receivables_risk["flag"]:
    print("⚠️ REVENUE / RECEIVABLES RISK")
else:
    print("✅ Revenue / Receivables Looks Reasonable")

print(revenue_receivables_risk["message"])


if cash_flow_risk["flag"]:
    print("⚠️ CASH FLOW CONVERSION RISK")
else:
    print("✅ Cash Flow Conversion Looks Reasonable")

print(cash_flow_risk["message"])


if inventory_risk["flag"]:
    print("⚠️ INVENTORY / REVENUE RISK")
else:
    print("✅ Inventory / Revenue Looks Reasonable")

print(inventory_risk["message"])


if dso_risk["flag"]:
    print("⚠️ DSO RISK")
else:
    print("✅ DSO Looks Reasonable")

print(dso_risk["message"])


if fcf_risk["flag"]:
    print("⚠️ FCF CONVERSION RISK")
else:
    print("✅ FCF Conversion Looks Reasonable")

print(fcf_risk["message"])


if current_ratio_risk["flag"]:
    print("⚠️ CURRENT RATIO RISK")
else:
    print("✅ Current Ratio Looks Reasonable")

print(current_ratio_risk["message"])


if debt_risk["flag"]:
    print("⚠️ DEBT GROWTH RISK")
else:
    print("✅ Debt Growth Looks Reasonable")

print(debt_risk["message"])


if liabilities_assets_risk["flag"]:
    print("⚠️ LIABILITIES / ASSETS RISK")
else:
    print("✅ Liabilities / Assets Looks Reasonable")

print(liabilities_assets_risk["message"])


print()
print("==============================")
print("FINANCIAL REPORTING RISK SCORE")
print("==============================")

print(f"Score: {score}/100")
print(f"Category: {category}")