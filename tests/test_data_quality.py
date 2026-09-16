from analysis.data_quality import assess_data_quality


def test_data_quality_requires_two_annual_periods_for_screening_readiness():
    financial_data = {
        "revenue": [{"year": 2025, "value": 100}],
        "net_income": [{"year": 2024, "value": 10}, {"year": 2025, "value": 12}],
        "assets": [{"year": 2024, "value": 90}, {"year": 2025, "value": 100}],
        "liabilities": [{"year": 2024, "value": 40}, {"year": 2025, "value": 45}],
        "receivables": [{"year": 2024, "value": 8}, {"year": 2025, "value": 9}],
        "operating_cash_flow": [{"year": 2024, "value": 15}, {"year": 2025, "value": 16}],
        "current_assets": [{"year": 2024, "value": 30}, {"year": 2025, "value": 32}],
        "current_liabilities": [{"year": 2024, "value": 25}, {"year": 2025, "value": 28}],
    }

    result = assess_data_quality(financial_data)

    assert result["coverage_percent"] == 100.0
    assert result["insufficient_history"] == ["Revenue"]
    assert result["screening_ready"] is False
    assert result["annual_period_counts"]["Revenue"] == 1


def test_data_quality_reports_missing_metrics():
    result = assess_data_quality({"revenue": [{"year": 2025, "value": 100}]})

    assert result["coverage_percent"] == 12.5
    assert "Net income" in result["missing"]
    assert result["screening_ready"] is False
