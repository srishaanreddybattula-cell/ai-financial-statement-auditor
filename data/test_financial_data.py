from data.financial_data import get_capex, get_debt, get_financial_data, get_fact


def test_get_financial_data_uses_receivables_key():
    company_facts = {
        "facts": {
            "us-gaap": {
                "AccountsReceivableNetCurrent": {
                    "units": {
                        "USD": [
                            {
                                "val": 100,
                                "form": "10-K",
                                "end": "2025-12-31",
                                "filed": "2026-02-01",
                            }
                        ]
                    }
                }
            }
        }
    }

    result = get_financial_data(company_facts)

    assert "receivables" in result
    assert "accounts_receivable" not in result
    assert result["receivables"][0]["value"] == 100


def test_get_fact_ignores_non_10k_filings():
    company_facts = {
        "facts": {
            "us-gaap": {
                "Revenue": {
                    "units": {
                        "USD": [
                            {
                                "val": 50,
                                "form": "10-Q",
                                "end": "2025-09-30",
                                "filed": "2025-11-01",
                            },
                            {
                                "val": 100,
                                "form": "10-K",
                                "end": "2025-12-31",
                                "filed": "2026-02-01",
                            },
                        ]
                    }
                }
            }
        }
    }

    result = get_fact(company_facts, "Revenue")

    assert len(result) == 1
    assert result[0]["value"] == 100


def test_get_capex_requires_full_year_period():
    company_facts = {
        "facts": {
            "us-gaap": {
                "PaymentsToAcquirePropertyPlantAndEquipment": {
                    "units": {
                        "USD": [
                            {
                                "val": 25,
                                "form": "10-K",
                                "start": "2025-01-01",
                                "end": "2025-12-31",
                                "filed": "2026-02-01",
                            },
                            {
                                "val": 5,
                                "form": "10-K",
                                "start": "2025-10-01",
                                "end": "2025-12-31",
                                "filed": "2026-02-01",
                            },
                        ]
                    }
                }
            }
        }
    }

    result = get_capex(company_facts)

    assert len(result) == 1
    assert result[0]["value"] == 25


def test_get_debt_combines_current_and_noncurrent_debt():
    company_facts = {
        "facts": {
            "us-gaap": {
                "LongTermDebtCurrent": {
                    "units": {
                        "USD": [
                            {
                                "val": 10,
                                "form": "10-K",
                                "end": "2025-12-31",
                                "filed": "2026-02-01",
                            }
                        ]
                    }
                },
                "LongTermDebtNoncurrent": {
                    "units": {
                        "USD": [
                            {
                                "val": 90,
                                "form": "10-K",
                                "end": "2025-12-31",
                                "filed": "2026-02-01",
                            }
                        ]
                    }
                },
            }
        }
    }

    result = get_debt(company_facts)

    assert len(result) == 1
    assert result[0]["value"] == 100
