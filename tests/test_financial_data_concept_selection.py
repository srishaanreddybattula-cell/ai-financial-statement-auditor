from data.financial_data import _get_fact_from_namespaces


def _fact(years):
    return {
        "units": {
            "USD": [
                {
                    "form": "10-K",
                    "start": f"{year}-01-01",
                    "end": f"{year}-12-31",
                    "filed": f"{year + 1}-02-01",
                    "val": year,
                    "accn": f"000000-{year}",
                }
                for year in years
            ]
        }
    }


def test_prefers_concept_reaching_latest_annual_year_over_longer_obsolete_history():
    company_facts = {
        "facts": {
            "us-gaap": {
                "OldRevenueTag": _fact(range(2010, 2018)),
                "CurrentRevenueTag": _fact(range(2020, 2026)),
            }
        }
    }

    result = _get_fact_from_namespaces(
        company_facts,
        ["OldRevenueTag", "CurrentRevenueTag"],
    )

    assert result[-1]["year"] == 2025


def test_keeps_candidate_order_when_latest_year_and_history_are_equal():
    company_facts = {
        "facts": {
            "us-gaap": {
                "PreferredTag": _fact(range(2022, 2026)),
                "FallbackTag": _fact(range(2022, 2026)),
            }
        }
    }

    result = _get_fact_from_namespaces(
        company_facts,
        ["PreferredTag", "FallbackTag"],
    )

    assert result[-1]["accn"] == "000000-2025"
