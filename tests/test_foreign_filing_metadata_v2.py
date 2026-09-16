from data.financial_data import ANNUAL_FORMS


def test_foreign_annual_forms_are_supported_by_the_data_layer():
    assert {"20-F", "40-F"}.issubset(ANNUAL_FORMS)


def test_foreign_filing_form_is_not_forced_to_10k():
    filing = {"form": "40-F"}
    assert filing.get("form", "annual report") == "40-F"
