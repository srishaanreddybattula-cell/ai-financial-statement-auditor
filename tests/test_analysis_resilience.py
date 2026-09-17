from analysis.pipeline import analyze_company
from reports.excel_report import build_excel_report
from reports.pdf_report import build_pdf_report


def _minimal_submissions():
    return {
        "filings": {
            "recent": {
                "form": ["20-F"],
                "accessionNumber": ["0000000000-26-000001"],
                "primaryDocument": ["annual.htm"],
                "filingDate": ["2026-05-01"],
                "reportDate": ["2026-03-31"],
            }
        }
    }


def _fact(value, year, form="20-F"):
    return {
        "units": {
            "USD": [
                {
                    "form": form,
                    "start": f"{year - 1}-04-01",
                    "end": f"{year}-03-31",
                    "filed": "2026-05-01",
                    "val": value,
                    "accn": "0000000000-26-000001",
                }
            ]
        }
    }


def test_sparse_foreign_annual_facts_produce_partial_analysis_instead_of_failing():
    company_facts = {
        "facts": {
            "ifrs-full": {
                "Revenue": _fact(100, 2026),
                "Assets": {
                    "units": {
                        "USD": [{
                            "form": "20-F",
                            "end": "2026-03-31",
                            "filed": "2026-05-01",
                            "val": 250,
                            "accn": "0000000000-26-000001",
                        }]
                    }
                },
            }
        }
    }

    result = analyze_company("1", _minimal_submissions(), company_facts)

    assert result["filing"]["form"] == "20-F"
    assert result["latest_year"] == 2026
    assert result["partial_analysis"] is True
    assert "risk_dimensions" in result
    assert "analysis_warnings" in result


def test_exports_use_source_filing_report_year():
    result = {
        "latest_year": 2017,
        "data_period_year": 2017,
        "risk_score": 10,
        "risk_category": "Low",
        "risk_dimensions": {"example": None},
        "score_breakdown": [],
        "findings": [],
        "financial_data": {},
        "peer_comparison": {"peer_count": 0, "message": "Unavailable"},
        "goodwill_analysis": {"goodwill_to_assets": None, "goodwill_change": None, "flag": False, "message": "Unavailable"},
        "filing": {
            "form": "10-K",
            "filing_date": "2026-02-01",
            "report_date": "2025-12-31",
            "primary_document": "annual.htm",
            "accession_number": "0000000000-26-000001",
            "sec_url": "https://www.sec.gov/",
        },
    }

    pdf = build_pdf_report(result, "Test Co", "TEST", "1")
    excel = build_excel_report(result, "Test Co", "TEST", "1")
    assert pdf.startswith(b"%PDF")
    assert excel[:2] == b"PK"
