from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


def build_excel_report(result, company_name, ticker, cik):
    workbook = Workbook()
    summary = workbook.active
    summary.title = "Summary"

    header_fill = PatternFill("solid", fgColor="E9EEF5")
    header_font = Font(bold=True)
    title_font = Font(bold=True, size=16)

    summary["A1"] = "Financial Reporting Risk Screening Report"
    summary["A1"].font = title_font
    summary.merge_cells("A1:D1")

    summary_rows = [
        ("Company", company_name),
        ("Ticker", ticker),
        ("CIK", cik),
        ("Latest annual period", result.get("latest_year", "N/A")),
        ("Screening score", result.get("risk_score", 0)),
        ("Prototype risk category", result.get("risk_category", "N/A")),
    ]

    for row_number, (label, value) in enumerate(summary_rows, start=3):
        summary.cell(row=row_number, column=1, value=label).font = header_font
        summary.cell(row=row_number, column=2, value=value)

    # The analysis pipeline stores the selected 10-K under "filing".
    # Keep the Excel report aligned with that canonical result structure.
    filing = result.get("filing") or {}
    summary["A10"] = "Source filing"
    summary["A10"].font = header_font
    source_rows = [
        ("Form", "10-K" if filing else "N/A"),
        ("Filed", filing.get("filing_date", "N/A")),
        ("Report date", filing.get("report_date", "N/A")),
        ("Primary document", filing.get("primary_document", "N/A")),
        ("SEC accession number", filing.get("accession_number", "N/A")),
        ("SEC source filing", filing.get("sec_url", "N/A")),
    ]
    for row_number, (label, value) in enumerate(source_rows, start=11):
        summary.cell(row=row_number, column=1, value=label).font = header_font
        cell = summary.cell(row=row_number, column=2, value=value)
        if label == "SEC source filing" and filing.get("sec_url"):
            cell.hyperlink = filing["sec_url"]
            cell.style = "Hyperlink"

    summary["A18"] = "Interpretation"
    summary["A18"].font = header_font
    summary["A19"] = (
        "This workbook is a prototype screening model for potential financial reporting risk indicators. "
        "A flagged indicator does not establish an accounting error, fraud, or material misstatement."
    )
    summary.merge_cells("A19:D20")
    summary["A19"].alignment = Alignment(wrap_text=True, vertical="top")

    _add_risk_dimensions_sheet(workbook, result)
    _add_findings_sheet(workbook, result)
    _add_data_quality_sheet(workbook, result)
    _add_financial_data_sheet(workbook, result)
    _add_goodwill_sheet(workbook, result)
    _add_peer_sheet(workbook, result)
    _add_policies_sheet(workbook, result)

    for sheet in workbook.worksheets:
        sheet.freeze_panes = "A2"
        for column_cells in sheet.columns:
            column_letter = get_column_letter(column_cells[0].column)
            max_length = 0
            for cell in column_cells:
                value = "" if cell.value is None else str(cell.value)
                max_length = max(max_length, len(value))
            sheet.column_dimensions[column_letter].width = min(max(max_length + 2, 12), 60)

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def _style_header(sheet):
    for cell in sheet[1]:
        cell.fill = PatternFill("solid", fgColor="E9EEF5")
        cell.font = Font(bold=True)


def _add_risk_dimensions_sheet(workbook, result):
    sheet = workbook.create_sheet("Risk Dimensions")
    sheet.append(["Dimension", "Risk level"])
    _style_header(sheet)
    for name, value in result.get("risk_dimensions", {}).items():
        sheet.append([name.replace("_", " ").title(), value])

    sheet.append([])
    sheet.append(["Score breakdown"])
    sheet.append(["Dimension", "Risk level", "Weight", "Contribution"])
    for cell in sheet[sheet.max_row]:
        cell.fill = PatternFill("solid", fgColor="E9EEF5")
        cell.font = Font(bold=True)

    for item in result.get("score_breakdown", []):
        sheet.append([
            item["dimension"].replace("_", " ").title(),
            item["risk_level"],
            item["weight"],
            item["contribution"],
        ])


def _add_findings_sheet(workbook, result):
    sheet = workbook.create_sheet("Key Findings")
    sheet.append(["Priority", "Finding", "Evidence", "Why it matters"])
    _style_header(sheet)
    findings = result.get("findings", [])
    for finding in findings:
        sheet.append([
            finding.get("priority", "N/A"),
            finding.get("title", "N/A"),
            finding.get("evidence", "N/A"),
            finding.get("why_it_matters", "N/A"),
        ])
    if not findings:
        sheet.append(["", "No screening findings were triggered by the current rules.", "", ""])


def _add_data_quality_sheet(workbook, result):
    sheet = workbook.create_sheet("Data Quality")
    sheet.append(["Metric", "Value"])
    _style_header(sheet)

    data_quality = result.get("data_quality", {})
    sheet.append(["Core metric coverage", data_quality.get("coverage_percent", 0)])
    sheet.append(["Coverage status", data_quality.get("status", "Unknown")])
    sheet.append(["Missing core metrics", ", ".join(data_quality.get("missing", [])) or "None"])
    sheet.append([
        "Explanation",
        "Coverage measures whether the core annual financial metrics needed by the screening model are available. It does not measure the accuracy or completeness of the underlying SEC filing.",
    ])


def _add_financial_data_sheet(workbook, result):
    sheet = workbook.create_sheet("Financial Data")
    financial_data = result.get("financial_data", {})
    fields = [
        ("Revenue", financial_data.get("revenue", [])),
        ("Net income", financial_data.get("net_income", [])),
        ("Assets", financial_data.get("assets", [])),
        ("Cash", financial_data.get("cash", [])),
        ("Liabilities", financial_data.get("liabilities", [])),
        ("Debt", financial_data.get("debt", [])),
        ("Receivables", financial_data.get("receivables", [])),
        ("Inventory", financial_data.get("inventory", [])),
        ("Operating cash flow", financial_data.get("operating_cash_flow", [])),
        ("Capital expenditures", financial_data.get("capital_expenditures", [])),
        ("Current assets", financial_data.get("current_assets", [])),
        ("Current liabilities", financial_data.get("current_liabilities", [])),
        ("Goodwill", financial_data.get("goodwill", [])),
    ]

    sheet.append([
        "Metric",
        "Year",
        "Value",
        "Form",
        "Filed",
        "SEC accession number",
        "Period start",
        "Period end",
        "SEC frame",
    ])
    _style_header(sheet)
    for metric, values in fields:
        for item in values:
            sheet.append([
                metric,
                item.get("year"),
                item.get("value"),
                item.get("form"),
                item.get("filed"),
                item.get("accn"),
                item.get("start"),
                item.get("end"),
                item.get("frame"),
            ])


def _add_goodwill_sheet(workbook, result):
    sheet = workbook.create_sheet("Goodwill Analysis")
    sheet.append(["Metric", "Value"])
    _style_header(sheet)

    goodwill = result.get("goodwill_analysis", {})
    if goodwill.get("goodwill_to_assets") is None:
        sheet.append(["Status", goodwill.get("message", "Not enough data to analyze goodwill.")])
        return

    sheet.append(["Goodwill / total assets", goodwill.get("goodwill_to_assets")])
    sheet.append(["Year-over-year goodwill change", goodwill.get("goodwill_change")])
    sheet.append([
        "Screening status",
        "Review suggested" if goodwill.get("flag") else "No threshold triggered",
    ])
    sheet.append(["Explanation", goodwill.get("message", "")])


def _add_peer_sheet(workbook, result):
    sheet = workbook.create_sheet("Peer Comparison")
    peer = result.get("peer_comparison", {})
    sheet.append(["Metric", "Company", "Peer median", "Risk direction", "Robust z-score", "Metric risk level"])
    _style_header(sheet)

    labels = {
        "receivables_to_revenue": "Receivables / Revenue",
        "dso": "DSO",
        "accrual_ratio": "Accrual Ratio",
        "current_ratio": "Current Ratio",
        "ocf_conversion": "OCF Conversion",
    }

    for metric, values in peer.get("metrics", {}).items():
        direction = "Higher is riskier" if values.get("risk_direction") == "higher" else "Lower is riskier"
        sheet.append([
            labels.get(metric, metric),
            values.get("company_value"),
            values.get("peer_median"),
            direction,
            values.get("z_score"),
            values.get("risk_level"),
        ])

    sheet.append([])
    sheet.append(["Peer count", peer.get("peer_count", 0)])
    sheet.append(["Comparison year", peer.get("comparison_year", "N/A")])
    sheet.append(["Peer deviation risk level", peer.get("risk_score", 0)])


def _add_policies_sheet(workbook, result):
    sheet = workbook.create_sheet("Accounting Policies")
    sheet.append(["Policy/topic", "Keywords or evidence"])
    _style_header(sheet)

    policy = result.get("policy_analysis") or {}
    for policy_name, matches in policy.get("policy_matches", {}).items():
        if matches:
            sheet.append([policy_name.replace("_", " ").title(), ", ".join(matches)])

    for topic, analysis in result.get("accounting_topics", {}).items():
        for evidence in analysis.get("evidence", []):
            sheet.append([topic, evidence])
