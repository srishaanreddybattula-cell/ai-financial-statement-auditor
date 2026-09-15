import streamlit as st

from analysis.findings import generate_findings
from analysis.pipeline import analyze_company
from analysis.risk_score import calculate_score_breakdown
from data.sec_api import get_company_submissions
from data.ticker_map import get_cik_from_ticker
from data.xbrl import get_company_facts
from data.normalizer import normalize_annual_data


st.set_page_config(
    page_title="AI Financial Statement Auditor",
    page_icon="📊",
    layout="wide"
)

st.title("AI Financial Statement Auditor")
st.caption("SEC-grounded financial reporting risk analysis — not an audit opinion or fraud detector.")

with st.form("company_form"):
    ticker_input = st.text_input("Company ticker", placeholder="AAPL")
    submitted = st.form_submit_button("Analyze company")

if submitted:
    ticker = ticker_input.upper().strip()

    if not ticker:
        st.warning("Enter a company ticker first.")
        st.stop()

    with st.spinner("Retrieving SEC filings and XBRL data..."):
        try:
            cik = get_cik_from_ticker(ticker)

            if cik is None:
                st.error(f"Could not find a company with ticker: {ticker}")
                st.stop()

            submissions = get_company_submissions(cik)
            company_facts = get_company_facts(cik)
            result = analyze_company(cik, submissions, company_facts)

        except Exception as exc:
            st.error(f"Analysis failed: {exc}")
            st.stop()

    company_name = submissions.get("name", ticker)

    st.subheader(company_name)
    st.write(f"Ticker: **{ticker}** · CIK: **{cik}**")

    score_col, category_col, year_col = st.columns(3)
    score_col.metric("Financial Reporting Risk Score", f"{result['risk_score']:.2f}/100")
    category_col.metric("Prototype Risk Category", result["risk_category"])
    year_col.metric("Latest Annual Period", result["latest_year"])

    st.info(
        "The score is a prototype screening model. A flagged indicator means the financial data or disclosures deserve further review; it does not establish an accounting error, fraud, or material misstatement."
    )

    findings = generate_findings(result)

    st.header("Key findings")

    if findings:
        st.caption(f"{len(findings)} item(s) identified for further review based on the current screening rules.")

        for finding in findings:
            with st.expander(f"{finding['priority']} priority — {finding['title']}"):
                st.write("**Evidence**")
                st.write(finding["evidence"])
                st.write("**Why it matters**")
                st.write(finding["why_it_matters"])
    else:
        st.success("No screening findings were triggered by the current rules.")

    st.header("Key financial signals")

    metrics = [
        ("Revenue growth", result["revenue_growth"], "%"),
        ("Receivables growth", result["receivables_growth"], "%"),
        ("Inventory growth", result["inventory_growth"], "%"),
        ("DSO change", result["working_capital"]["dso_change"], "%"),
        ("Current ratio", result["working_capital"]["current_ratio"], ""),
        ("OCF conversion", result["cash_flow"]["cash_flow_conversion"], "%"),
        ("FCF conversion", result["cash_flow"]["fcf_conversion"], "%"),
        ("Accrual ratio", result["accruals"]["accrual_ratio"], ""),
    ]

    cols = st.columns(4)
    for index, (label, value, suffix) in enumerate(metrics):
        if value is None:
            display = "N/A"
        elif suffix == "%":
            display = f"{value:.2f}%"
        else:
            display = f"{value:.2f}"
        cols[index % 4].metric(label, display)

    st.header("Financial trends")

    financial_data = result["financial_data"]
    revenue_data = normalize_annual_data(financial_data["revenue"])
    net_income_data = normalize_annual_data(financial_data["net_income"])
    operating_cash_flow_data = normalize_annual_data(
        financial_data["operating_cash_flow"]
    )

    trend_years = sorted(
        set(item["year"] for item in revenue_data)
        & set(item["year"] for item in net_income_data)
        & set(item["year"] for item in operating_cash_flow_data)
    )[-5:]

    trend_rows = []

    for year in trend_years:
        revenue_item = next(
            (item for item in revenue_data if item["year"] == year), None
        )
        net_income_item = next(
            (item for item in net_income_data if item["year"] == year), None
        )
        ocf_item = next(
            (item for item in operating_cash_flow_data if item["year"] == year),
            None
        )

        if revenue_item and net_income_item and ocf_item:
            trend_rows.append(
                {
                    "Year": str(year),
                    "Revenue ($B)": revenue_item["value"] / 1_000_000_000,
                    "Net Income ($B)": net_income_item["value"] / 1_000_000_000,
                    "Operating Cash Flow ($B)": ocf_item["value"] / 1_000_000_000,
                }
            )

    if trend_rows:
        import pandas as pd

        trend_df = pd.DataFrame(trend_rows).set_index("Year")
        st.line_chart(trend_df, y_label="USD billions")
    else:
        st.warning("Not enough annual data was available to display financial trends.")

    st.header("Historical anomaly review")
    historical_anomalies = result.get("historical_anomalies", [])
    growth_accelerations = result.get("growth_accelerations", [])

    if historical_anomalies:
        st.warning(
            f"{len(historical_anomalies)} historical revenue-growth anomaly/anomalies were identified for further review."
        )
        for anomaly in historical_anomalies:
            with st.expander(f"{anomaly['year']} — unusual revenue growth"):
                st.write(f"**Revenue growth:** {anomaly['growth']:.2f}%")
                st.write(f"**Historical z-score:** {anomaly['z_score']:.2f}")
                st.write(anomaly["message"])
    else:
        st.success("No historical revenue-growth anomalies were identified by the current model.")

    if growth_accelerations:
        st.write("**Large changes in annual growth rate**")
        for acceleration in growth_accelerations:
            st.write(
                f"- {acceleration['year']}: growth changed by "
                f"{acceleration['growth_change']:.2f} percentage points "
                f"({acceleration['prior_growth']:.2f}% → {acceleration['growth']:.2f}%)."
            )
    else:
        st.caption("No large year-over-year changes in revenue growth were identified by the current threshold.")

    st.header("Risk dimensions")
    risk_dimensions = result["risk_dimensions"]
    risk_rows = [
        (name.replace("_", " ").title(), value)
        for name, value in risk_dimensions.items()
    ]
    st.dataframe(risk_rows, column_config={"0": "Dimension", "1": "Risk level"}, hide_index=True, use_container_width=True)

    st.subheader("How the risk score is calculated")
    st.caption("Each dimension is capped at 100, multiplied by its model weight, and added to produce the 0–100 screening score.")

    breakdown_rows = []
    for item in calculate_score_breakdown(risk_dimensions):
        breakdown_rows.append(
            {
                "Dimension": item["dimension"].replace("_", " ").title(),
                "Risk level": item["risk_level"],
                "Weight": f"{item['weight']}%",
                "Score contribution": item["contribution"],
            }
        )

    st.dataframe(
        breakdown_rows,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Risk level": st.column_config.NumberColumn(format="%.0f"),
            "Score contribution": st.column_config.NumberColumn(format="%.2f"),
        },
    )
    st.metric("Total weighted score", f"{result['risk_score']:.2f}/100")

    st.header("Accounting policy review")
    policy = result.get("policy_analysis")

    if policy is None:
        st.write("No latest 10-K policy section was available.")
    else:
        st.write("Policy keyword matches are displayed as evidence for review. Normal accounting disclosures are not automatically treated as misconduct.")
        for policy_name, matches in policy["policy_matches"].items():
            if matches:
                st.write(f"**{policy_name.replace('_', ' ').title()}:** {', '.join(matches)}")

        for topic, analysis in result["accounting_topics"].items():
            if analysis["evidence"]:
                with st.expander(topic):
                    st.write("Judgment:", analysis["judgment"])
                    st.write("Uncertainty:", analysis["uncertainty"])
                    st.write("Potential material impact:", analysis["material_impact"])
                    for evidence in analysis["evidence"]:
                        st.write(f"- {evidence}")

    if result.get("filing"):
        st.header("Source filing")
        filing = result["filing"]
        st.write(f"Form 10-K · filed {filing['filing_date']} · report date {filing['report_date']}")
        st.write(f"Primary document: `{filing['primary_document']}`")

st.divider()
st.caption("Prototype for financial reporting risk screening. Always review the underlying SEC filing and consult a qualified professional for accounting or investment decisions.")