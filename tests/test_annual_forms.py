from data.financial_data import _annual_value_records


def test_foreign_annual_forms_include_20f_and_40f_but_exclude_6k():
    fact = {
        "units": {
            "USD": [
                {
                    "val": 100,
                    "form": "20-F",
                    "filed": "2026-03-01",
                    "accn": "20f",
                    "start": "2025-01-01",
                    "end": "2025-12-31",
                },
                {
                    "val": 90,
                    "form": "40-F",
                    "filed": "2025-03-01",
                    "accn": "40f",
                    "start": "2024-01-01",
                    "end": "2024-12-31",
                },
                {
                    "val": 5,
                    "form": "6-K",
                    "filed": "2026-02-15",
                    "accn": "6k",
                    "start": "2025-12-31",
                    "end": "2026-01-31",
                },
            ]
        }
    }

    result = _annual_value_records(fact)

    assert [item["form"] for item in result] == ["40-F", "20-F"]
    assert [item["value"] for item in result] == [90, 100]
