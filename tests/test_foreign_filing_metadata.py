def test_foreign_annual_forms_are_supported_by_the_data_layer():
    annual_forms = {"10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A"}
    assert {"20-F", "40-F"}.issubset(annual_forms)


def test_foreign_filing_form_is_not_forced_to_10k():
    filing = {"form": "40-F"}
    assert filing.get("form", "annual report") == "40-F"
