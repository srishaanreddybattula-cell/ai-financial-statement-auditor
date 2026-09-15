from analysis.accounting_policies import analyze_accounting_policies


sample_text = """
Revenue is recognized when performance obligations are satisfied.
The company accounts for stock-based compensation.
The company has operating leases and lease liabilities.
Goodwill is tested for impairment.
The company reports income taxes and deferred tax assets.
Fair value measurements include Level 1, Level 2, and Level 3 inputs.
"""


result = analyze_accounting_policies(sample_text)


print("ACCOUNTING POLICY ANALYSIS")
print("==============================")

print("POLICY TOPICS FOUND:")

for policy, keywords in result["policy_matches"].items():
    if keywords:
        print(f"{policy}: {', '.join(keywords)}")

print()
print("POLICY FLAGS:")

for policy, flagged in result["policy_flags"].items():
    print(f"{policy}: {flagged}")

print()
print(f"Accounting policy risk score: {result['risk_score']}/100")