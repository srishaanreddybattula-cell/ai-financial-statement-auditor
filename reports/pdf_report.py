from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _format_risk_value(value):
    """Format an optional risk value without crashing on unavailable data."""
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "N/A"


def build_pdf_report(result, company_name, ticker, cik):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title=f"Financial Reporting Risk Screening - {company_name}",
        author="AI Financial Statement Auditor",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], alignment=TA_CENTER,
        fontSize=20, leading=24, spaceAfter=8,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle", parent=styles["Normal"], alignment=TA_CENTER,
        fontSize=9, leading=12, textColor=colors.grey, spaceAfter=16,
    )
    section_style = ParagraphStyle(
        "Section", parent=styles["Heading2"], fontSize=13,
        leading=16, spaceBefore=12, spaceAfter=7,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["BodyText"], fontSize=9,
        leading=12, spaceAfter=5,
    )

    story = []
    story.append(Paragraph("Financial Reporting Risk Screening Report", title_style))
    story.append(Paragraph(
        f"{company_name} ({ticker}) · CIK {cik} · Latest annual period {result.get('latest_year', 'N/A')}",
        subtitle_style,
    ))

    score = float(result.get("risk_score", 0))
    category = result.get("risk_category", "N/A")
    score_table = Table(
        [["Screening score", "Prototype category"], [f"{score:.2f} / 100", category]],
        colWidths=[3.4 * inch, 3.4 * inch],
    )
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9EEF5")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B8C2CC")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(score_table)

    story.append(Paragraph("Important interpretation", section_style))
    story.append(Paragraph(
        "This report presents a prototype screening model for potential financial reporting risk indicators. A flagged indicator does not establish an accounting error, fraud, or material misstatement. Underlying SEC filings should be reviewed before drawing conclusions.",
        body_style,
    ))

    findings = result.get("findings") or []
    story.append(Paragraph("Key findings", section_style))
    if findings:
        finding_rows = [["Priority", "Finding", "Evidence"]]
        for finding in findings:
            finding_rows.append([
                finding.get("priority", "N/A"),
                finding.get("title", "N/A"),
                finding.get("evidence", "N/A"),
            ])
        finding_table = Table(finding_rows, colWidths=[0.85 * inch, 2.2 * inch, 3.75 * inch], repeatRows=1)
        finding_table.setStyle(_table_style())
        story.append(finding_table)
    else:
        story.append(Paragraph("No screening findings were triggered by the current rules.", body_style))

    story.append(Paragraph("Risk dimensions", section_style))
    dimensions = result.get("risk_dimensions", {})
    dimension_rows = [["Dimension", "Risk level"]]
    for name, value in dimensions.items():
        dimension_rows.append([name.replace("_", " ").title(), _format_risk_value(value)])
    dimension_table = Table(dimension_rows, colWidths=[4.8 * inch, 2.0 * inch], repeatRows=1)
    dimension_table.setStyle(_table_style())
    story.append(dimension_table)

    story.append(Paragraph("Score breakdown", section_style))
    breakdown_rows = [["Dimension", "Risk", "Weight", "Contribution"]]
    for item in result.get("score_breakdown", []):
        breakdown_rows.append([
            item["dimension"].replace("_", " ").title(),
            _format_risk_value(item.get("risk_level")),
            f"{item.get('weight', 0)}%",
            _format_risk_value(item.get("contribution")),
        ])
    if len(breakdown_rows) > 1:
        breakdown_table = Table(
            breakdown_rows,
            colWidths=[3.1 * inch, 1.0 * inch, 1.0 * inch, 1.7 * inch],
            repeatRows=1,
        )
        breakdown_table.setStyle(_table_style())
        story.append(breakdown_table)

    peer = result.get("peer_comparison", {})
    story.append(Paragraph("Peer comparison", section_style))
    if peer.get("peer_count", 0):
        peer_risk = _format_risk_value(peer.get("risk_score"))
        story.append(Paragraph(
            f"Compared with {peer['peer_count']} selected peers using annual period {peer.get('comparison_year', 'N/A')}. Peer deviation risk level: {peer_risk}/100.",
            body_style,
        ))
        peer_rows = [["Metric", "Company", "Peer median", "Risk direction", "Risk level"]]
        for metric, values in peer.get("metrics", {}).items():
            peer_rows.append([
                metric.replace("_", " ").title(),
                f"{values['company_value']:.2f}",
                f"{values['peer_median']:.2f}",
                "Higher is riskier" if values.get("risk_direction") == "higher" else "Lower is riskier",
                _format_risk_value(values.get("risk_level")),
            ])
        peer_table = Table(peer_rows, colWidths=[1.75 * inch, 1.1 * inch, 1.1 * inch, 1.55 * inch, 1.0 * inch], repeatRows=1)
        peer_table.setStyle(_table_style())
        story.append(peer_table)
    else:
        story.append(Paragraph("No peer comparison was available.", body_style))

    story.append(Paragraph("Accounting policy review", section_style))
    policy = result.get("policy_analysis")
    if policy:
        matched = []
        for policy_name, keywords in policy.get("policy_matches", {}).items():
            if keywords:
                matched.append(f"{policy_name.replace('_', ' ').title()}: {', '.join(keywords)}")
        if matched:
            for item in matched:
                story.append(Paragraph(item, body_style))
        else:
            story.append(Paragraph("No configured policy keywords were matched.", body_style))
    else:
        story.append(Paragraph("No latest annual filing policy section was available.", body_style))

    goodwill = result.get("goodwill_analysis", {})
    story.append(Paragraph("Goodwill analysis", section_style))
    if goodwill.get("goodwill_to_assets") is None:
        story.append(Paragraph(goodwill.get("message", "Not enough data to analyze goodwill."), body_style))
    else:
        goodwill_rows = [
            ["Metric", "Value"],
            ["Goodwill / total assets", f"{goodwill['goodwill_to_assets']:.2f}%"],
            ["Year-over-year goodwill change", "N/A" if goodwill.get("goodwill_change") is None else f"{goodwill['goodwill_change']:.2f}%"],
            ["Screening status", "Review suggested" if goodwill.get("flag") else "No threshold triggered"],
        ]
        goodwill_table = Table(goodwill_rows, colWidths=[4.8 * inch, 2.0 * inch], repeatRows=1)
        goodwill_table.setStyle(_table_style())
        story.append(goodwill_table)
        story.append(Paragraph(goodwill.get("message", ""), body_style))

    filing = result.get("filing")
    story.append(Paragraph("Source filing", section_style))
    if filing:
        story.append(Paragraph(
            f"Form {filing.get('form', 'annual report')} · filed {filing.get('filing_date', 'N/A')} · report date {filing.get('report_date', 'N/A')} · primary document {filing.get('primary_document', 'N/A')}",
            body_style,
        ))
        sec_url = filing.get("sec_url")
        if sec_url:
            story.append(Paragraph(
                f'<link href="{sec_url}" color="#1565C0"><u>Open source filing on SEC.gov</u></link>',
                body_style,
            ))
    else:
        story.append(Paragraph("Source filing information was not available.", body_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Prepared by AI Financial Statement Auditor. Screening output only; review the underlying SEC filing and consult a qualified professional for accounting or investment decisions.",
        subtitle_style,
    ))

    document.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def _table_style():
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9EEF5")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B8C2CC")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("LEADING", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ])
