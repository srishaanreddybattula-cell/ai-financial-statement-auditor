from analysis.anomaly_detection import (
    detect_growth_acceleration,
    detect_historical_growth_anomalies,
)
from analysis.findings import generate_findings
from analysis.pipeline import find_latest_annual_filing
from analysis.risk_score import calculate_risk_score, get_risk_category
from data.financial_data import get_fact, get_financial_data, get_goodwill
from data.normalizer import normalize_annual_data


def test_normalize_annual_data_keeps_latest_filing():
    data = [
        {"year": 2024, "value": 100, "filed": "2024-10-01"},
        {"year": 2024, "value": 110, "filed": "2024-11-01"},
        {"year": 2025, "value": 120, "filed": "2025-10-01"},
    ]
    result = normalize_annual_data(data)
    assert result == [
        {"year": 2024, "value": 110, "filed": "2024-11-01"},
        {"year": 2025, "value": 120, "filed": "2025-10-01"},
    ]


def test_risk_score_zero_and_full_scale():
    dimensions = {
        "revenue_quality": 0,
        "accrual_quality": 0,
        "cash_flow_quality": 0,
        "working_capital": 0,
        "accounting_policy_risk": 0,
        "leverage_liquidity": 0,
        "peer_deviation": 0,
    }
    assert calculate_risk_score(dimensions) == 0
    assert get_risk_category(0) == "Very Low"
    dimensions = {name: 100 for name in dimensions}
    assert calculate_risk_score(dimensions) == 100
    assert get_risk_category(100) == "Very High"


def test_historical_anomaly_detection_requires_enough_history():
    data = [
        {"year": 2023, "value": 100},
        {"year": 2024, "value": 110},
        {"year": 2025, "value": 121},
    ]
    assert detect_historical_growth_anomalies(data) == []


def test_growth_acceleration_detects_large_change():
    data = [
        {"year": 2022, "value": 100},
        {"year": 2023, "value": 105},
        {"year": 2024, "value": 130},
    ]
    result = detect_growth_acceleration(data, change_threshold=10)
    assert len(result) == 1
    assert result[0]["year"] == 2024
    assert result[0]["growth_change"] > 10


def test_findings_detect_receivables_and_dso_signals():
    result = {
        "revenue_growth": 5.0,
        "receivables_growth": 20.0,
        "working_capital": {
            "dso": 35.0,
            "dso_change": 12.0,
            "current_ratio": 1.1,
        },
        "cash_flow": {},
        "accruals": {},
        "policy_analysis": None,
        "accounting_topics": {},
    }
    findings = generate_findings(result)
    titles = {finding["title"] for finding in findings}
    assert "Receivables are growing faster than revenue" in titles
    assert "Days sales outstanding increased" in titles


def test_findings_detect_profit_margin_expansion():
    result = {
        "revenue_growth": 5.0,
        "receivables_growth": 5.0,
        "working_capital": {},
        "cash_flow": {
            "net_income_growth": 30.0,
            "ocf_growth": 20.0,
            "cash_flow_conversion": 95.0,
        },
        "accruals": {},
        "financial_data": {
            "revenue": [
                {"year": 2024, "value": 100.0},
                {"year": 2025, "value": 105.0},
            ],
            "net_income": [
                {"year": 2024, "value": 100.0},
                {"year": 2025, "value": 130.0},
            ],
        },
        "policy_analysis": None,
        "accounting_topics": {},
    }
    findings = generate_findings(result)
    titles = {finding["title"] for finding in findings}
    assert "Profit margin expanded materially" in titles


def test_financial_fact_preserves_sec_provenance():
    company_facts = {
        "facts": {
            "us-gaap": {
                "TestMetric": {
                    "units": {
                        "USD": [
                            {
                                "val": 123,
                                "form": "10-K",
                                "filed": "2025-10-31",
                                "accn": "0000000000-25-000001",
                                "frame": "CY2025",
                                "start": "2024-09-29",
                                "end": "2025-09-27",
                            }
                        ]
                    }
                }
            }
        }
    }
    result = get_fact(company_facts, "TestMetric")
    assert result == [
        {
            "year": 2025,
            "value": 123,
            "filed": "2025-10-31",
            "start": "2024-09-29",
            "end": "2025-09-27",
            "form": "10-K",
            "accn": "0000000000-25-000001",
            "accession_number": "0000000000-25-000001",
            "frame": "CY2025",
        }
    ]


def test_goodwill_ignores_stale_facts():
    company_facts = {
        "facts": {
            "us-gaap": {
                "Goodwill": {
                    "units": {
                        "USD": [
                            {
                                "val": 900,
                                "form": "10-K",
                                "filed": "2017-11-01",
                                "accn": "old",
                                "end": "2017-09-30",
                            }
                        ]
                    }
                },
                "Assets": {
                    "units": {
                        "USD": [
                            {
                                "val": 100000,
                                "form": "10-K",
                                "filed": "2025-10-31",
                                "accn": "new",
                                "end": "2025-09-27",
                            },
                            {
                                "val": 90000,
                                "form": "10-K",
                                "filed": "2024-11-01",
                                "accn": "prior",
                                "end": "2024-09-28",
                            },
                        ]
                    }
                },
            }
        }
    }
    assert get_goodwill(company_facts) == []


def test_ifrs_financial_facts_are_supported():
    company_facts = {
        "facts": {
            "ifrs-full": {
                "Revenue": {
                    "units": {
                        "USD": [
                            {
                                "val": 200,
                                "form": "20-F",
                                "filed": "2026-03-01",
                                "accn": "foreign-2026",
                                "start": "2025-01-01",
                                "end": "2025-12-31",
                            },
                            {
                                "val": 180,
                                "form": "20-F",
                                "filed": "2025-03-01",
                                "accn": "foreign-2025",
                                "start": "2024-01-01",
                                "end": "2024-12-31",
                            },
                        ]
                    }
                },
                "ProfitLoss": {
                    "units": {
                        "USD": [
                            {
                                "val": 40,
                                "form": "20-F",
                                "filed": "2026-03-01",
                                "accn": "foreign-2026",
                                "start": "2025-01-01",
                                "end": "2025-12-31",
                            },
                            {
                                "val": 35,
                                "form": "20-F",
                                "filed": "2025-03-01",
                                "accn": "foreign-2025",
                                "start": "2024-01-01",
                                "end": "2024-12-31",
                            },
                        ]
                    }
                },
                "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities": {
                    "units": {
                        "USD": [
                            {
                                "val": -30,
                                "form": "20-F",
                                "filed": "2026-03-01",
                                "accn": "foreign-2026",
                                "start": "2025-01-01",
                                "end": "2025-12-31",
                            },
                            {
                                "val": -25,
                                "form": "20-F",
                                "filed": "2025-03-01",
                                "accn": "foreign-2025",
                                "start": "2024-01-01",
                                "end": "2024-12-31",
                            },
                        ]
                    }
                },
            }
        }
    }
    result = get_financial_data(company_facts)
    assert result["revenue"][-1]["value"] == 200
    assert result["revenue"][-1]["form"] == "20-F"
    assert result["net_income"][-1]["value"] == 40
    assert result["capital_expenditures"][-1]["value"] == -30


def test_latest_annual_filing_supports_foreign_forms():
    submissions = {
        "filings": {
            "recent": {
                "form": ["6-K", "20-F", "8-K"],
                "accessionNumber": ["a", "0000123456-26-000001", "b"],
                "primaryDocument": ["x.htm", "annual.htm", "y.htm"],
                "filingDate": ["2026-01-01", "2026-02-01", "2026-03-01"],
                "reportDate": ["2025-12-01", "2025-12-31", "2026-03-01"],
            }
        }
    }
    filing = find_latest_annual_filing(submissions, 123456)
    assert filing["form"] == "20-F"
    assert filing["accession_number"] == "0000123456-26-000001"
    assert filing["sec_url"].endswith("/000012345626000001/annual.htm")
