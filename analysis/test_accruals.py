from data.ticker_map import get_cik_from_ticker
from data.xbrl import get_company_facts
from data.financial_data import get_financial_data

from analysis.accruals import assess_accrual_quality


ticker = "AAPL"

cik = get_cik_from_ticker(ticker)
company_facts = get_company_facts(cik)
financial_data = get_financial_data(company_facts)


net_income = financial_data["net_income"][-1]["value"]
operating_cash_flow = financial_data["operating_cash_flow"][-1]["value"]
assets = financial_data["assets"][-1]["value"]


result = assess_accrual_quality(
    net_income,
    operating_cash_flow,
    assets
)


print("APPLE ACCRUAL QUALITY")
print("==============================")
print(f"Accrual ratio: {result['accrual_ratio']:.4f}")
print(
    f"Earnings vs cash difference: "
    f"{result['earnings_cash_difference']:.2f}%"
)
print(f"Accrual risk score: {result['risk_score']}/100")