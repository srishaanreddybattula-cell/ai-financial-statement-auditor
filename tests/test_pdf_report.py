from reports.pdf_report import build_pdf_report


def test_pdf_report_handles_unavailable_risk_dimensions():
    result = {
        "latest_year": 2025,
        "risk_score": 20.0,
        "risk_category": "Low",
        "risk_dimensions": {
            "revenue_quality": 20.0,
            "accrual_quality": None,
            "cash_flow_quality": None,
            "working_capital": None,
            "accounting_policy_risk": None,
            "leverage_liquidity": None,
            "peer_deviation": None,
        },
        "score_breakdown": [
            {
                "dimension": "revenue_quality",
                "risk_level": 20.0,
                "weight": 20,
                "contribution": 20.0,
                "available": True,
            },
            {
                "dimension": "peer_deviation",
                "risk_level": None,
                "weight": 10,
                "contribution": None,
                "available": False,
            },
        ],
        "findings": [],
        "peer_comparison": {},
        "policy_analysis": None,
        "goodwill_analysis": {"goodwill_to_assets": None, "message": "Not available."},
        "filing": None,
    }

    pdf_bytes = build_pdf_report(result, "Example Corp", "EXM", "0000000000")

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 1000
