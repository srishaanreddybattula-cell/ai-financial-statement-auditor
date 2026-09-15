import streamlit as st

from analysis.pipeline import analyze_company
from data.sec_api import get_company_submissions
from data.ticker_map import get_cik_from_ticker
from data.xbrl import get_company_facts


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

    st.header("Risk dimensions")
    risk_dimensions = result["risk_dimensions"]
    risk_rows = [
        (name.replace("_", " ").title(), value)
        for name, value in risk_dimensions.items()
    ]
    st.dataframe(risk_rows, column_config={"0": "Dimension", "1": "Risk level"}, hide_index=True, use_container_width=True)

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
