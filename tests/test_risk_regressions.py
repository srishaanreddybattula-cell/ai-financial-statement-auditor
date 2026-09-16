from analysis.cash_flow import calculate_free_cash_flow
from analysis.risk_assessment import assess_policy_risk, assess_risk_dimensions
from analysis.risk_score import calculate_risk_score, calculate_score_coverage
from data.financial_data import get_debt


def test_free_cash_flow_handles_negative_sec_capex_sign():
    assert calculate_free_cash_flow(100, -30) == 70
    assert calculate_free_cash_flow(100, 30) == 70


def test_missing_risk_dimensions_are_not_treated_as_zero_risk():
    dimensions = {
        "revenue_quality": 20,
        "accrual_quality": None,
        "cash_flow_quality": None,
        "working_capital": None,
        "accounting_policy_risk": None,
        "leverage_liquidity": None,
        "peer_deviation": None,
    }
    assert calculate_risk_score(dimensions) == 20
    assert calculate_score_coverage(dimensions) == 20


def test_leverage_risk_uses_debt_and_liability_ratios():
    dimensions = assess_risk_dimensions({
        "revenue_vs_receivables": {"flag": False},
        "dso": {"flag": False},
        "inventory_vs_revenue": {"flag": False},
        "current_ratio": {"value": 0.7},
        "debt_to_assets": {"value": 0.6},
        "liabilities_to_assets": {"value": 0.85},
    })
    assert dimensions["leverage_liquidity"] == 100


def test_policy_risk_is_unavailable_when_no_filing_topics_exist():
    assert assess_policy_risk({}) is None


def test_debt_combines_current_and_noncurrent_annual_facts():
    company_facts = {
        "facts": {
            "us-gaap": {
                "LongTermDebtCurrent": {
                    "units": {
                        "USD": [
                            {
                                "val": 25,
                                "form": "10-K",
                                "filed": "2026-02-01",
                                "accn": "current",
                                "end": "2025-12-31",
                            }
                        ]
                    }
                },
                "LongTermDebtNoncurrent": {
                    "units": {
                        "USD": [
                            {
                                "val": 75,
                                "form": "10-K",
                                "filed": "2026-02-01",
                                "accn": "noncurrent",
                                "end": "2025-12-31",
                            }
                        ]
                    }
                },
            }
        }
    }
    debt = get_debt(company_facts)
    assert debt[-1]["value"] == 100
    assert debt[-1]["current"] == 25
    assert debt[-1]["noncurrent"] == 75
