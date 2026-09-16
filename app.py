import streamlit as st
from pathlib import Path

from analysis.findings import generate_findings
from analysis.pipeline import analyze_company
from analysis.peer_pipeline import add_peer_analysis
from analysis.risk_score import calculate_score_breakdown
from analysis.data_quality import assess_data_quality
from data.sec_api import get_company_submissions
from data.ticker_map import get_company_from_query
from data.xbrl import get_company_facts
from data.normalizer import normalize_annual_data
from reports.excel_report import build_excel_report
from reports.pdf_report import build_pdf_report


st.set_page_config(page_title="Aurevia | Financial Intelligence", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

# Load the custom dark dashboard theme from the repository.
st.markdown(f"<style>{Path('theme.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# Branded sidebar
with st.sidebar:
    st.markdown("<div class='brand'><span class='brand-mark'>◈</span><span>Aurevia</span></div>", unsafe_allow_html=True)
    st.caption("Financial intelligence, grounded in SEC data")
    st.divider()
    st.markdown("### ◈  Home")
    st.markdown("### ⌕  Company Analysis")
    st.markdown("### ▣  Financial Statements")
    st.markdown("### ◫  Key Metrics")
    st.markdown("### ⇄  Compare Companies")
    st.markdown("### ♧  Saved Reports")
    st.markdown("<div class='sidebar-footer'><b>Smarter finance.</b><br>Deeper insights.</div>", unsafe_allow_html=True)

st.markdown("<div class='eyebrow'>AI FINANCIAL INTELLIGENCE</div>", unsafe_allow_html=True)
st.title("Welcome to Aurevia")
st.caption("Analyze a company's financials with SEC-grounded AI-powered insights.")

with st.form("company_form"):
    company_input = st.text_input("Company name or ticker", placeholder="Apple, Microsoft, NVIDIA, Tesla, ASML, Alibaba, or AAPL", label_visibility="collapsed")
    submitted = st.form_submit_button("Analyze  →", use_container_width=False)

if submitted:
    company_query = company_input.strip()

    if not company_query:
        st.warning("Enter a company name or ticker first.")
        st.stop()

    with st.spinner("Finding the company and retrieving SEC filings and XBRL data..."):
        try:
            company = get_company_from_query(company_query)
            if company is None:
                st.error(f"Could not uniquely find an SEC-reporting company for: {company_query}. Try a more specific company name or its ticker.")
                st.stop()
            ticker = company["ticker"]
            cik = company["cik"]
            submissions = get_company_submissions(cik)
            company_facts = get_company_facts(cik)
            result = analyze_company(cik, submissions, company_facts)
            result = add_peer_analysis(result, ticker)
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")
            st.stop()

    company_name = submissions.get("name", company["name"])
    st.subheader(company_name)
    ticker_display = ticker or "No ticker mapped"
    st.write(f"Ticker: **{ticker_display}** · CIK: **{cik}**")

    score_col, category_col, year_col = st.columns(3)
    score_col.metric("Financial Reporting Risk Score", f"{result['risk_score']:.2f}/100")
    category_col.metric("Prototype Risk Category", result["risk_category"])
    year_col.metric("Latest Annual Period", result["latest_year"])
    st.info("The score is a prototype screening model. A flagged indicator means the financial data or disclosures deserve further review; it does not establish an accounting error, fraud, or material misstatement.")

    st.subheader("Risk score overview")
    score = max(0.0, min(100.0, float(result["risk_score"])))
    st.progress(score / 100)
    st.caption(f"Current screening score: **{score:.2f}/100** · Prototype category: **{result['risk_category']}**")

    findings = generate_findings(result)
    result["findings"] = findings
    result["score_breakdown"] = calculate_score_breakdown(result["risk_dimensions"])

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

    st.header("Data quality & coverage")
    data_quality = result.get("data_quality") or assess_data_quality(result.get("financial_data", {}))
    quality_col1, quality_col2 = st.columns(2)
    quality_col1.metric("Core metric coverage", f"{data_quality['coverage_percent']:.0f}%")
    quality_col2.metric("Coverage status", data_quality["status"])
    st.progress(data_quality["coverage_percent"] / 100)
    if data_quality["missing"]:
        st.warning("Missing core metrics: " + ", ".join(data_quality["missing"]))
    else:
        st.success("All core metrics required by the screening model are available.")
    st.caption("Coverage measures whether the core annual financial metrics needed by the screening model are available. It does not measure the accuracy or completeness of the underlying SEC filing.")

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

    st.header("SEC data provenance")
    st.caption("These fields identify the SEC filing metadata retained with the annual XBRL facts used by the screening model.")
    provenance_rows = []
    provenance_labels = {
        "revenue": "Revenue",
        "net_income": "Net income",
        "assets": "Assets",
        "receivables": "Receivables",
        "operating_cash_flow": "Operating cash flow",
        "capital_expenditures": "Capital expenditures",
        "goodwill": "Goodwill",
    }
    for key, label in provenance_labels.items():
        annual_data = normalize_annual_data(result.get("financial_data", {}).get(key, []))
        if not annual_data:
            continue
        item = annual_data[-1]
        provenance_rows.append({
            "Metric": label,
            "Fiscal year": item.get("year"),
            "Form": item.get("form") or "N/A",
            "Filed": item.get("filed") or "N/A",
            "Accession number": item.get("accn") or "N/A",
            "Period end": item.get("end") or "N/A",
        })
    debt_data = normalize_annual_data(result.get("financial_data", {}).get("debt", []))
    if debt_data:
        item = debt_data[-1]
        provenance_rows.append({
            "Metric": "Debt",
            "Fiscal year": item.get("year"),
            "Form": item.get("form") or "N/A",
            "Filed": item.get("filed") or "N/A",
            "Accession number": item.get("accn") or "N/A",
            "Period end": item.get("end") or "N/A",
        })
    if provenance_rows:
        st.dataframe(provenance_rows, hide_index=True, width="stretch")
    else:
        st.info("No SEC provenance metadata was available for the extracted annual facts.")

    st.header("Goodwill analysis")
    goodwill = result.get("goodwill_analysis", {})
    goodwill_col1, goodwill_col2, goodwill_col3 = st.columns(3)
    goodwill_to_assets = goodwill.get("goodwill_to_assets")
    goodwill_change = goodwill.get("goodwill_change")
    goodwill_flag = goodwill.get("flag", False)
    goodwill_col1.metric("Goodwill / total assets", f"{goodwill_to_assets:.2f}%" if goodwill_to_assets is not None else "N/A")
    goodwill_col2.metric("Year-over-year goodwill change", f"{goodwill_change:.2f}%" if goodwill_change is not None else "N/A")
    goodwill_col3.metric("Screening status", "Review indicated" if goodwill_flag else "No threshold triggered")
    st.caption("The goodwill screen is a prototype rule for impairment and acquisition-accounting review. A large goodwill balance or decline does not by itself establish an impairment or accounting error.")
    st.write(goodwill.get("message", "Not enough data to analyze goodwill."))

    st.header("Financial trends")
    financial_data = result["financial_data"]
    revenue_data = normalize_annual_data(financial_data["revenue"])
    net_income_data = normalize_annual_data(financial_data["net_income"])
    operating_cash_flow_data = normalize_annual_data(financial_data["operating_cash_flow"])
    trend_years = sorted(set(item["year"] for item in revenue_data) & set(item["year"] for item in net_income_data) & set(item["year"] for item in operating_cash_flow_data))[-5:]
    trend_rows = []
    for year in trend_years:
        revenue_item = next((item for item in revenue_data if item["year"] == year), None)
        net_income_item = next((item for item in net_income_data if item["year"] == year), None)
        ocf_item = next((item for item in operating_cash_flow_data if item["year"] == year), None)
        if revenue_item and net_income_item and ocf_item:
            trend_rows.append({"Year": str(year), "Revenue ($B)": revenue_item["value"] / 1_000_000_000, "Net Income ($B)": net_income_item["value"] / 1_000_000_000, "Operating Cash Flow ($B)": ocf_item["value"] / 1_000_000_000})
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
        st.warning(f"{len(historical_anomalies)} historical revenue-growth anomaly/anomalies were identified for further review.")
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
            st.write(f"- {acceleration['year']}: growth changed by {acceleration['growth_change']:.2f} percentage points ({acceleration['prior_growth']:.2f}% → {acceleration['growth']:.2f}%).")
    else:
        st.caption("No large year-over-year changes in revenue growth were identified by the current threshold.")

    st.header("Risk dimensions")
    risk_dimensions = result["risk_dimensions"]
    risk_rows = [(name.replace("_", " ").title(), value) for name, value in risk_dimensions.items()]
    st.dataframe(risk_rows, column_config={"0": "Dimension", "1": "Risk level"}, hide_index=True, width="stretch")
    st.subheader("How the risk score is calculated")
    st.caption("Each dimension is capped at 100, multiplied by its model weight, and added to produce the 0–100 screening score.")
    breakdown_rows = [{"Dimension": item["dimension"].replace("_", " ").title(), "Risk level": item["risk_level"], "Weight": f"{item['weight']}%", "Score contribution": item["contribution"]} for item in result["score_breakdown"]]
    st.dataframe(breakdown_rows, hide_index=True, width="stretch", column_config={"Risk level": st.column_config.NumberColumn(format="%.0f"), "Score contribution": st.column_config.NumberColumn(format="%.2f")})
    st.metric("Total weighted score", f"{result['risk_score']:.2f}/100")

    st.header("Peer comparison")
    peer_comparison = result.get("peer_comparison", {})
    peer_count = peer_comparison.get("peer_count", 0)
    comparison_year = peer_comparison.get("comparison_year")
    if peer_count == 0:
        st.info(peer_comparison.get("message", "No peer comparison was available."))
    else:
        st.caption(f"Compared with {peer_count} selected peers using the same annual period: {comparison_year}. Peer deviation is a screening signal based on differences from the peer median." if comparison_year else f"Compared with {peer_count} selected peers. Peer deviation is a screening signal based on differences from the peer median.")
        peer_tickers = [peer.get("ticker") for peer in peer_comparison.get("peers", []) if peer.get("ticker")]
        if peer_tickers:
            st.write(f"**Peers:** {', '.join(peer_tickers)}")
        metric_labels = {"receivables_to_revenue": "Receivables / Revenue", "dso": "DSO", "accrual_ratio": "Accrual Ratio", "current_ratio": "Current Ratio", "ocf_conversion": "OCF Conversion"}
        risk_direction_labels = {"higher": "Higher is riskier", "lower": "Lower is riskier"}
        peer_rows = [{"Metric": metric_labels.get(metric, metric), "Company": values["company_value"], "Peer median": values["peer_median"], "Risk direction": risk_direction_labels.get(values.get("risk_direction"), "Not specified"), "Robust z-score": values["z_score"], "Metric risk level": values["risk_level"]} for metric, values in peer_comparison.get("metrics", {}).items()]
        if peer_rows:
            st.dataframe(peer_rows, hide_index=True, width="stretch", column_config={"Company": st.column_config.NumberColumn(format="%.2f"), "Peer median": st.column_config.NumberColumn(format="%.2f"), "Robust z-score": st.column_config.NumberColumn(format="%.2f"), "Metric risk level": st.column_config.NumberColumn(format="%.0f")})
        st.metric("Peer deviation risk level", f"{peer_comparison['risk_score']:.2f}/100")
        st.caption(peer_comparison.get("message", ""))

    st.header("Accounting policy review")
    policy = result.get("policy_analysis")
    if policy is None:
        st.write("No latest annual policy section was available.")
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
        st.write(f"Form {filing.get('form', 'annual report')} · filed {filing['filing_date']} · report date {filing['report_date']}")
        st.write(f"Primary document: `{filing['primary_document']}`")
        if filing.get("sec_url"):
            st.link_button("Open filing on SEC.gov", filing["sec_url"])

    st.header("Download report")
    report_col1, report_col2 = st.columns(2)
    with report_col1:
        pdf_bytes = build_pdf_report(result, company_name, ticker, cik)
        st.download_button("Download PDF report", data=pdf_bytes, file_name=f"{ticker or cik}_financial_reporting_risk_report.pdf", mime="application/pdf")
    with report_col2:
        excel_bytes = build_excel_report(result, company_name, ticker, cik)
        st.download_button("Download Excel report", data=excel_bytes, file_name=f"{ticker or cik}_financial_reporting_risk_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.divider()
st.caption("Aurevia is a prototype for SEC-grounded financial reporting risk screening. Always review the underlying SEC filing and consult a qualified professional for accounting or investment decisions.")
