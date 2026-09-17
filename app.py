import streamlit as st
from pathlib import Path

from analysis.data_quality import assess_data_quality
from analysis.findings import generate_findings
from analysis.peer_pipeline import add_peer_analysis
from analysis.pipeline import analyze_company
from analysis.risk_score import calculate_score_breakdown, calculate_score_coverage
from data.normalizer import normalize_annual_data
from data.sec_api import get_company_submissions
from data.ticker_map import get_company_from_query
from data.xbrl import get_company_facts
from reports.excel_report import build_excel_report
from reports.pdf_report import build_pdf_report


st.set_page_config(
    page_title="Aurevia | Financial Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(f"<style>{Path('theme.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
st.markdown(
    """
    <style>
    @media (max-width: 900px) {
        .main .block-container { padding-left: 1rem; padding-right: 1rem; }
        section[data-testid="stSidebar"] { max-width: 82vw; min-width: 250px; }
        [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

NAV_ITEMS = [
    ("home", "◈  Home"),
    ("company_analysis", "⌕  Company Analysis"),
    ("financial_statements", "▣  Financial Statements"),
    ("key_metrics", "◫  Key Metrics"),
    ("compare_companies", "⇄  Compare Companies"),
    ("saved_reports", "♧  Saved Reports"),
]

if "nav_page" not in st.session_state:
    st.session_state.nav_page = "home"
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "analysis_error" not in st.session_state:
    st.session_state.analysis_error = None
if "report_files" not in st.session_state:
    st.session_state.report_files = {}

with st.sidebar:
    st.markdown("<div class='brand'><span class='brand-mark'>◈</span><span>Aurevia</span></div>", unsafe_allow_html=True)
    st.caption("Financial intelligence, grounded in SEC data")
    st.divider()
    for page_key, page_label in NAV_ITEMS:
        if st.button(
            page_label,
            key=f"nav_{page_key}",
            use_container_width=True,
            type="primary" if st.session_state.nav_page == page_key else "secondary",
        ):
            st.session_state.nav_page = page_key
            st.rerun()
    st.markdown("<div class='sidebar-footer'><b>Smarter finance.</b><br>Deeper insights.</div>", unsafe_allow_html=True)


def render_search_form(key_suffix):
    with st.form(f"company_form_{key_suffix}"):
        company_input = st.text_input(
            "Company name or ticker",
            placeholder="Apple, Microsoft, NVIDIA, Tesla, ASML, Alibaba, or AAPL",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Analyze  →", use_container_width=False)

    if not submitted:
        return

    query = company_input.strip()
    # Clear the previous company before any new request so a failed request can
    # never leave the user looking at stale Tesla/Apple/etc. results.
    st.session_state.analysis_result = None
    st.session_state.analysis_company_name = None
    st.session_state.analysis_ticker = None
    st.session_state.analysis_cik = None
    st.session_state.analysis_submissions = None
    st.session_state.analysis_error = None

    if not query:
        st.session_state.analysis_error = "Enter a company name or ticker first."
        return

    try:
        with st.spinner("Finding the company and retrieving SEC filings and XBRL data..."):
            company = get_company_from_query(query)
            if company is None:
                raise ValueError(
                    f"Could not uniquely find an SEC-reporting company for: {query}. "
                    "Try a more specific company name or ticker."
                )
            ticker = company.get("ticker")
            cik = company["cik"]
            submissions = get_company_submissions(cik)
            company_facts = get_company_facts(cik)
            result = analyze_company(cik, submissions, company_facts)
            result = add_peer_analysis(result, ticker)
            result["findings"] = generate_findings(result)
            result["score_breakdown"] = calculate_score_breakdown(result["risk_dimensions"])

        company_name = submissions.get("name", company.get("name", "Unknown company"))
        st.session_state.analysis_result = result
        st.session_state.analysis_company_name = company_name
        st.session_state.analysis_ticker = ticker
        st.session_state.analysis_cik = cik
        st.session_state.analysis_submissions = submissions
    except Exception as exc:
        st.session_state.analysis_error = f"Analysis could not be completed: {exc}"


def render_home():
    st.markdown("<div class='eyebrow'>AI FINANCIAL INTELLIGENCE</div>", unsafe_allow_html=True)
    st.title("Welcome to Aurevia")
    st.caption("Analyze a company's financials with SEC-grounded AI-powered insights.")
    render_search_form("home")

    result = st.session_state.analysis_result
    if st.session_state.analysis_error:
        st.error(st.session_state.analysis_error)
        st.info("Your previous analysis was cleared. Enter another company above to retry.")
        return
    if result is None:
        st.info("Start with a company name or ticker. The app will use the latest annual SEC filing it can identify and show data coverage when individual metrics are unavailable.")
        return

    render_company_header(result)
    st.subheader("Analysis ready")
    st.write("Use the sidebar to inspect findings, financial statements, key metrics, peer comparison, or generate reports.")


def render_company_header(result):
    company_name = st.session_state.get("analysis_company_name") or "Company"
    ticker = st.session_state.get("analysis_ticker") or "No ticker mapped"
    cik = st.session_state.get("analysis_cik") or "N/A"
    score = result.get("risk_score", 0)
    st.subheader(company_name)
    st.write(f"Ticker: **{ticker}** · CIK: **{cik}**")
    c1, c2, c3 = st.columns(3)
    c1.metric("Financial Reporting Risk Score", f"{float(score):.2f}/100")
    c2.metric("Prototype Risk Category", result.get("risk_category", "N/A"))
    c3.metric("Latest Annual Period", result.get("latest_year", "N/A"))
    st.info("The score is a prototype screening model. A flagged indicator means the financial data or disclosures deserve further review; it does not establish an accounting error, fraud, or material misstatement.")


def render_company_analysis(result):
    render_company_header(result)
    coverage = calculate_score_coverage(result.get("risk_dimensions", {}))
    if result.get("partial_analysis"):
        st.warning("This is a partial analysis. Metrics that cannot be supported by the selected annual SEC filing are shown as N/A rather than stopping the analysis.")
    st.subheader("Risk score overview")
    st.progress(max(0.0, min(100.0, float(result.get("risk_score", 0)))) / 100)
    st.caption(f"Risk model coverage: **{coverage:.0f}%**")
    if coverage < 100:
        st.warning("Some risk dimensions do not have enough underlying data. They are excluded from the score rather than treated as zero risk.")

    st.header("Key findings")
    findings = result.get("findings", [])
    if findings:
        st.caption(f"{len(findings)} item(s) identified for further review based on the current screening rules.")
        for finding in findings:
            with st.expander(f"{finding.get('priority', 'N/A')} priority — {finding.get('title', 'Finding')}"):
                st.write("**Evidence**")
                st.write(finding.get("evidence", "N/A"))
                st.write("**Why it matters**")
                st.write(finding.get("why_it_matters", "N/A"))
    else:
        st.success("No screening findings were triggered by the current rules.")

    st.header("Data quality & coverage")
    quality = result.get("data_quality") or assess_data_quality(result.get("financial_data", {}))
    q1, q2 = st.columns(2)
    q1.metric("Core metric coverage", f"{quality.get('coverage_percent', 0):.0f}%")
    q2.metric("Coverage status", quality.get("status", "N/A"))
    st.progress(max(0.0, min(100.0, float(quality.get("coverage_percent", 0)))) / 100)
    if quality.get("missing"):
        st.warning("Missing core metrics: " + ", ".join(quality["missing"]))
    if quality.get("insufficient_history"):
        st.warning("Limited annual history for: " + ", ".join(quality["insufficient_history"]))
    if not quality.get("missing") and not quality.get("insufficient_history"):
        st.success("All core metrics required by the screening model have usable annual history.")

    warnings = result.get("analysis_warnings", [])
    if warnings:
        st.header("Data availability notes")
        for warning in warnings:
            st.write(f"• {warning}")

    st.header("Source filing")
    filing = result.get("filing")
    if filing:
        st.write(f"Form **{filing.get('form', 'annual report')}** · filed **{filing.get('filing_date', 'N/A')}** · report date **{filing.get('report_date', 'N/A')}**")
        st.write(f"Primary document: `{filing.get('primary_document', 'N/A')}`")
        if filing.get("sec_url"):
            st.link_button("Open filing on SEC.gov", filing["sec_url"])
    else:
        st.info("No annual source filing was found in the available SEC submission history.")


def render_financial_statements(result):
    render_company_header(result)
    financial_data = result.get("financial_data", {})
    st.header("Annual financial data")
    rows = []
    for metric, values in financial_data.items():
        if not isinstance(values, list):
            continue
        for item in normalize_annual_data(values):
            rows.append({
                "Metric": metric.replace("_", " ").title(),
                "Fiscal year": item.get("year"),
                "Value": item.get("value"),
                "Form": item.get("form") or "N/A",
                "Filed": item.get("filed") or "N/A",
                "Period end": item.get("end") or "N/A",
            })
    if rows:
        st.dataframe(rows, hide_index=True, width="stretch")
    else:
        st.info("No annual financial facts were available.")

    st.header("Financial trends")
    revenue = normalize_annual_data(financial_data.get("revenue", []))
    net_income = normalize_annual_data(financial_data.get("net_income", []))
    ocf = normalize_annual_data(financial_data.get("operating_cash_flow", []))
    revenue_by_year = {x["year"]: x["value"] for x in revenue}
    income_by_year = {x["year"]: x["value"] for x in net_income}
    ocf_by_year = {x["year"]: x["value"] for x in ocf}
    years = sorted(set(revenue_by_year) & set(income_by_year) & set(ocf_by_year))[-5:]
    if years:
        import pandas as pd
        trend = pd.DataFrame({
            "Revenue ($B)": [revenue_by_year[y] / 1_000_000_000 for y in years],
            "Net Income ($B)": [income_by_year[y] / 1_000_000_000 for y in years],
            "Operating Cash Flow ($B)": [ocf_by_year[y] / 1_000_000_000 for y in years],
        }, index=[str(y) for y in years])
        st.line_chart(trend, y_label="USD billions")
    else:
        st.info("Not enough overlapping annual revenue, net income, and operating cash flow data to display a trend.")


def render_key_metrics(result):
    render_company_header(result)
    wc = result.get("working_capital", {}) or {}
    cf = result.get("cash_flow", {}) or {}
    accruals = result.get("accruals", {}) or {}
    financial_data = result.get("financial_data", {}) or {}

    def value_for_year(key):
        values = normalize_annual_data(financial_data.get(key, []))
        target = result.get("data_period_year")
        for item in values:
            if item.get("year") == target:
                return item.get("value")
        return None

    assets = value_for_year("assets")
    debt = value_for_year("debt")
    liabilities = value_for_year("liabilities")
    debt_assets = debt / assets if debt is not None and assets not in (None, 0) else None
    liabilities_assets = liabilities / assets if liabilities is not None and assets not in (None, 0) else None

    metrics = [
        ("Revenue growth", result.get("revenue_growth"), "%"),
        ("Receivables growth", result.get("receivables_growth"), "%"),
        ("Inventory growth", result.get("inventory_growth"), "%"),
        ("DSO change", wc.get("dso_change"), "%"),
        ("Current ratio", wc.get("current_ratio"), "number"),
        ("Debt / assets", debt_assets, "percent"),
        ("Liabilities / assets", liabilities_assets, "percent"),
        ("OCF conversion", cf.get("cash_flow_conversion"), "%"),
        ("FCF conversion", cf.get("fcf_conversion"), "%"),
        ("Accrual ratio", accruals.get("accrual_ratio"), "number"),
    ]
    st.header("Key financial signals")
    cols = st.columns(4)
    for index, (label, value, fmt) in enumerate(metrics):
        if value is None:
            display = "N/A"
        elif fmt == "%":
            display = f"{value:.2f}%"
        elif fmt == "percent":
            display = f"{value:.2%}"
        else:
            display = f"{value:.2f}"
        cols[index % 4].metric(label, display)

    st.header("Risk dimensions")
    dimensions = result.get("risk_dimensions", {})
    dimension_rows = [{"Dimension": name.replace("_", " ").title(), "Risk level": "N/A" if value is None else value} for name, value in dimensions.items()]
    st.dataframe(dimension_rows, hide_index=True, width="stretch")
    st.subheader("How the risk score is calculated")
    st.caption("Available dimensions are capped at 100 and weighted by the prototype model. Unavailable dimensions are excluded from the denominator.")
    breakdown = []
    for item in result.get("score_breakdown", []):
        breakdown.append({
            "Dimension": item.get("dimension", "N/A").replace("_", " ").title(),
            "Risk level": "N/A" if item.get("risk_level") is None else item.get("risk_level"),
            "Model weight": f"{item.get('weight', 0)}%",
            "Normalized weight": f"{item.get('normalized_weight', 0):.2f}%",
            "Score contribution": "N/A" if item.get("contribution") is None else item.get("contribution"),
            "Data available": "Yes" if item.get("available") else "No",
        })
    st.dataframe(breakdown, hide_index=True, width="stretch")


def render_compare(result):
    render_company_header(result)
    peer = result.get("peer_comparison", {}) or {}
    st.header("Peer comparison")
    if not peer.get("peer_count"):
        st.info(peer.get("message", "No peer comparison was available."))
        return
    st.caption(f"Compared with {peer.get('peer_count')} selected peers using annual period {peer.get('comparison_year', 'N/A')}.")
    tickers = [p.get("ticker") for p in peer.get("peers", []) if p.get("ticker")]
    if tickers:
        st.write("**Peers:** " + ", ".join(tickers))
    labels = {
        "receivables_to_revenue": "Receivables / Revenue",
        "dso": "DSO",
        "accrual_ratio": "Accrual Ratio",
        "current_ratio": "Current Ratio",
        "ocf_conversion": "OCF Conversion",
    }
    rows = []
    for metric, values in peer.get("metrics", {}).items():
        rows.append({
            "Metric": labels.get(metric, metric),
            "Company": values.get("company_value", "N/A"),
            "Peer median": values.get("peer_median", "N/A"),
            "Risk direction": "Higher is riskier" if values.get("risk_direction") == "higher" else "Lower is riskier" if values.get("risk_direction") == "lower" else "N/A",
            "Robust z-score": values.get("z_score", "N/A"),
            "Metric risk level": values.get("risk_level", "N/A"),
        })
    if rows:
        st.dataframe(rows, hide_index=True, width="stretch")
    st.metric("Peer deviation risk level", f"{float(peer.get('risk_score', 0)):.2f}/100")
    st.caption(peer.get("message", ""))


def render_saved_reports(result):
    render_company_header(result)
    st.header("Generate reports")
    st.caption("Reports are generated only after you explicitly request them. Normal dashboard rendering never builds a PDF or Excel workbook.")
    ticker = st.session_state.get("analysis_ticker") or st.session_state.get("analysis_cik") or "company"
    company_name = st.session_state.get("analysis_company_name") or "Company"
    cik = st.session_state.get("analysis_cik")
    report_key = str(ticker)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Generate PDF report", key="generate_pdf", use_container_width=True):
            try:
                st.session_state.report_files.setdefault(report_key, {})["pdf"] = build_pdf_report(result, company_name, ticker, cik)
                st.success("PDF report generated successfully.")
            except Exception as exc:
                st.error(f"PDF report could not be generated: {exc}")
    with c2:
        if st.button("Generate Excel report", key="generate_excel", use_container_width=True):
            try:
                st.session_state.report_files.setdefault(report_key, {})["excel"] = build_excel_report(result, company_name, ticker, cik)
                st.success("Excel report generated successfully.")
            except Exception as exc:
                st.error(f"Excel report could not be generated: {exc}")

    files = st.session_state.report_files.get(report_key, {})
    if files.get("pdf"):
        st.download_button("Download PDF report", data=files["pdf"], file_name=f"{ticker}_financial_reporting_risk_report.pdf", mime="application/pdf", key="download_pdf")
    if files.get("excel"):
        st.download_button("Download Excel report", data=files["excel"], file_name=f"{ticker}_financial_reporting_risk_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="download_excel")

    if not files:
        st.info("No reports have been generated for this analysis yet.")


def render_page():
    page = st.session_state.nav_page
    result = st.session_state.analysis_result

    if page == "home":
        render_home()
        return

    if page == "company_analysis":
        st.markdown("<div class='eyebrow'>COMPANY ANALYSIS</div>", unsafe_allow_html=True)
        st.title("Company Analysis")
        render_search_form("company_analysis")
    elif result is None:
        st.title(dict(NAV_ITEMS)[page].split("  ", 1)[-1])
        st.info("Run a company analysis from Home or Company Analysis first. The result will remain available while you switch sections.")
        return

    if page == "company_analysis":
        result = st.session_state.analysis_result
        if st.session_state.analysis_error:
            st.error(st.session_state.analysis_error)
            st.info("Enter another company above to retry.")
            return
        render_company_analysis(result)
    elif page == "financial_statements":
        st.title("Financial Statements")
        render_financial_statements(result)
    elif page == "key_metrics":
        st.title("Key Metrics")
        render_key_metrics(result)
    elif page == "compare_companies":
        st.title("Compare Companies")
        render_compare(result)
    elif page == "saved_reports":
        st.title("Saved Reports")
        render_saved_reports(result)


render_page()
st.divider()
st.caption("Aurevia is a prototype for SEC-grounded financial reporting risk screening. Always review the underlying SEC filing and consult a qualified professional for accounting or investment decisions.")
