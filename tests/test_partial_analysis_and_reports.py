from reports.excel_report import build_excel_report
from reports.pdf_report import build_pdf_report
from analysis.pipeline import find_latest_annual_filing


def partial_result():
    return {
        "latest_year": 2025,
        "data_period_year": 2025,
        "risk_score": 42.5,
        "risk_category": "Moderate",
        "risk_dimensions": {
            "revenue_quality": 20,
            "accrual_quality": None,
            "cash_flow_quality": 30,
            "working_capital": None,
            "accounting_policy_risk": None,
            "leverage_liquidity": 10,
            "peer_deviation": None,
        },
        "score_breakdown": [
            {"dimension": "revenue_quality", "risk_level": 20, "weight": 20, "normalized_weight": 50, "contribution": 10, "available": True},
            {"dimension": "accrual_quality", "risk_level": None, "weight": 15, "normalized_weight": 0, "contribution": None, "available": False},
        ],
        "peer_comparison": {"peer_count": 0, "message": "Peer comparison unavailable."},
        "goodwill_analysis": {"goodwill_to_assets": None, "goodwill_change": None, "flag": False, "message": "Not enough data."},
        "findings": [],
        "financial_data": {},
        "filing": {
            "form": "20-F",
            "accession_number": "0000000000-25-000001",
            "primary_document": "annual.htm",
            "filing_date": "2026-02-20",
            "report_date": "2025-12-31",
            "sec_url": "https://www.sec.gov/Archives/edgar/data/1/annual.htm",
        },
        "analysis_warnings": ["Some metrics are unavailable."],
    }


def test_pdf_report_handles_unavailable_dimensions():
    data = build_pdf_report(partial_result(), "Test Co", "TEST", "1")
    assert data.startswith(b"%PDF")
    assert len(data) > 1000


def test_excel_report_handles_unavailable_dimensions():
    data = build_excel_report(partial_result(), "Test Co", "TEST", "1")
    assert data[:2] == b"PK"
    assert len(data) > 1000


def test_latest_annual_filing_supports_20f():
    submissions = {
        "filings": {
            "recent": {
                "form": ["10-Q", "20-F", "20-F/A"],
                "accessionNumber": ["a", "b", "c"],
                "primaryDocument": ["q.htm", "annual.htm", "annual-amend.htm"],
                "filingDate": ["2026-01-01", "2026-02-01", "2026-03-01"],
                "reportDate": ["2025-09-30", "2025-12-31", "2025-12-31"],
            }
        }
    }
    filing = find_latest_annual_filing(submissions, 123)
    assert filing["form"] == "20-F/A"
    assert filing["report_date"] == "2025-12-31"
