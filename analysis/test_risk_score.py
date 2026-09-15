from analysis.risk_score import calculate_risk_score
from analysis.risk_score import get_risk_category


risk_dimensions = {
    "revenue_quality": 60,
    "accrual_quality": 20,
    "cash_flow_quality": 10,
    "working_capital": 40,
    "accounting_policy_risk": 30,
    "leverage_liquidity": 20,
    "peer_deviation": 50
}


score = calculate_risk_score(risk_dimensions)
category = get_risk_category(score)


print("FINANCIAL REPORTING RISK SCORE")
print("==============================")
print(f"Score: {score}/100")
print(f"Category: {category}")