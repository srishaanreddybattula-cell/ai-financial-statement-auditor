def generate_findings(result):
    findings = []

    revenue_growth = result.get("revenue_growth")
    receivables_growth = result.get("receivables_growth")
    working_capital = result.get("working_capital", {})
    cash_flow = result.get("cash_flow", {})
    accruals = result.get("accruals", {})

    if revenue_growth is not None and receivables_growth is not None:
        difference = receivables_growth - revenue_growth
        if difference >= 10:
            findings.append({
                "priority": "High",
                "title": "Receivables are growing faster than revenue",
                "evidence": (
                    f"Receivables grew {receivables_growth:.2f}% while revenue grew "
                    f"{revenue_growth:.2f}%, a difference of {difference:.2f} percentage points."
                ),
                "why_it_matters": (
                    "A sustained gap can indicate that reported sales are converting to "
                    "cash more slowly and warrants review of revenue recognition, customer "
                    "terms, collections, and receivable aging."
                ),
            })

    dso_change = working_capital.get("dso_change")
    dso = working_capital.get("dso")
    if dso_change is not None and dso_change >= 10:
        findings.append({
            "priority": "High",
            "title": "Days sales outstanding increased",
            "evidence": (
                f"DSO is {dso:.2f} days and increased {dso_change:.2f}% from the prior year."
            ),
            "why_it_matters": (
                "A rising DSO can signal slower collections or changes in customer or "
                "contract terms. It should be reviewed alongside receivable aging and "
                "revenue-recognition disclosures."
            ),
        })

    current_ratio = working_capital.get("current_ratio")
    if current_ratio is not None and current_ratio < 1:
        findings.append({
            "priority": "Medium",
            "title": "Current liabilities exceed current assets",
            "evidence": (
                f"The current ratio is {current_ratio:.2f}, meaning current liabilities "
                "are greater than current assets."
            ),
            "why_it_matters": (
                "This is primarily a liquidity observation rather than evidence of an "
                "accounting error. Review short-term obligations, cash resources, and "
                "working-capital disclosures."
            ),
        })

    ocf_conversion = cash_flow.get("cash_flow_conversion")
    ocf_growth = cash_flow.get("ocf_growth")
    net_income_growth = cash_flow.get("net_income_growth")
    if (
        ocf_growth is not None
        and net_income_growth is not None
        and net_income_growth - ocf_growth >= 15
    ):
        findings.append({
            "priority": "Medium",
            "title": "Net income growth outpaced operating cash flow",
            "evidence": (
                f"Net income grew {net_income_growth:.2f}% while operating cash flow "
                f"changed {ocf_growth:.2f}%. OCF conversion was {ocf_conversion:.2f}%"
                if ocf_conversion is not None
                else (
                    f"Net income grew {net_income_growth:.2f}% while operating cash flow "
                    f"changed {ocf_growth:.2f}%."
                )
            ),
            "why_it_matters": (
                "A divergence between earnings and operating cash flow can arise from "
                "working-capital movements and other timing effects. Review the cash-flow "
                "statement and major changes in operating assets and liabilities."
            ),
        })

    financial_data = result.get("financial_data", {})
    revenue_data = sorted(financial_data.get("revenue", []), key=lambda item: item.get("year", 0))
    net_income_data = sorted(financial_data.get("net_income", []), key=lambda item: item.get("year", 0))
    if len(revenue_data) >= 2 and len(net_income_data) >= 2:
        latest_revenue = revenue_data[-1].get("value")
        previous_revenue = revenue_data[-2].get("value")
        latest_net_income = net_income_data[-1].get("value")
        previous_net_income = net_income_data[-2].get("value")
        if (
            latest_revenue is not None
            and previous_revenue not in (None, 0)
            and latest_net_income is not None
            and previous_net_income not in (None, 0)
        ):
            latest_margin = (latest_net_income / latest_revenue) * 100
            previous_margin = (previous_net_income / previous_revenue) * 100
            margin_change = latest_margin - previous_margin
            if net_income_growth is None:
                net_income_growth = ((latest_net_income - previous_net_income) / abs(previous_net_income)) * 100
            if net_income_growth - revenue_growth >= 20 and margin_change >= 3:
                findings.append({
                    "priority": "Low",
                    "title": "Profit margin expanded materially",
                    "evidence": (
                        f"Net income growth ({net_income_growth:.2f}%) exceeded revenue growth "
                        f"({revenue_growth:.2f}%) by at least 20 percentage points, while the "
                        f"profit margin increased from {previous_margin:.2f}% to {latest_margin:.2f}%."
                    ),
                    "why_it_matters": (
                        "A material increase in profitability can have ordinary business explanations, "
                        "such as pricing, product mix, cost reductions, or tax effects. It is included as "
                        "a low-priority screening signal so the underlying income-statement drivers can be reviewed."
                    ),
                })

    accrual_risk = accruals.get("risk_score", 0)
    if accrual_risk >= 50:
        findings.append({
            "priority": "Medium",
            "title": "Accrual quality warrants review",
            "evidence": (
                f"The prototype accrual-quality component produced a risk level of "
                f"{accrual_risk}/100."
            ),
            "why_it_matters": (
                "Large differences between accounting earnings and operating cash flow "
                "can require additional review of accruals and non-cash items."
            ),
        })

    historical_anomalies = result.get("historical_anomalies", [])
    for anomaly in historical_anomalies:
        findings.append({
            "priority": "Medium",
            "title": f"Unusual historical revenue growth in {anomaly['year']}",
            "evidence": anomaly["message"],
            "why_it_matters": (
                "A growth rate that is unusual relative to the company's own history "
                "deserves context. Review business conditions, acquisitions, divestitures, "
                "pricing, volume, and revenue-recognition disclosures for that period."
            ),
        })

    growth_accelerations = result.get("growth_accelerations", [])
    for anomaly in growth_accelerations:
        findings.append({
            "priority": "Low",
            "title": f"Revenue growth changed sharply in {anomaly['year']}",
            "evidence": anomaly["message"],
            "why_it_matters": (
                "A sharp change in growth can have ordinary business explanations. "
                "Comparing the change with company disclosures helps distinguish a "
                "business shift from an accounting-related issue."
            ),
        })

    policy = result.get("policy_analysis")
    topics = result.get("accounting_topics", {})
    if policy and topics:
        for topic, analysis in topics.items():
            if (
                analysis.get("judgment")
                and analysis.get("uncertainty")
                and analysis.get("material_impact")
            ):
                findings.append({
                    "priority": "Medium",
                    "title": f"Accounting estimate requires focused review: {topic}",
                    "evidence": (
                        "The latest 10-K discussion contains language indicating "
                        "management judgment, uncertainty, and potential material impact."
                    ),
                    "why_it_matters": (
                        "An estimate involving judgment, uncertainty, and potential material "
                        "impact is more sensitive to assumptions. Review the underlying "
                        "disclosure, assumptions, and changes from prior periods."
                    ),
                })

    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    findings.sort(key=lambda item: priority_order.get(item["priority"], 3))
    return findings
