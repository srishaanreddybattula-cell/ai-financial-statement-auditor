from analysis.anomaly_detection import (
    detect_growth_acceleration,
    detect_historical_growth_anomalies,
)
from analysis.findings import generate_findings
from analysis.risk_score import calculate_risk_score, get_risk_category
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
