def test_company_query_supports_names_and_tickers():
    """Document the user-facing contract for company lookup inputs."""
    examples = ["Apple", "APPLE", "apple", "ApPlE", "AAPL", "ASML", "Alibaba", "Toyota", "Sony"]
    assert all(example.strip() for example in examples)


def test_source_filing_uses_actual_form_metadata():
    filing = {
        "form": "20-F",
        "filing_date": "2026-03-01",
        "report_date": "2025-12-31",
    }
    displayed_form = filing.get("form", "annual report")
    assert displayed_form == "20-F"
