from data.ticker_map import _normalize_query


def test_company_input_is_case_insensitive_for_common_forms():
    values = ["Apple", "APPLE", "apple", "ApPlE"]
    assert {_normalize_query(value) for value in values} == {"apple"}


def test_company_input_accepts_ticker_style_values():
    assert _normalize_query("AAPL") == "aapl"
    assert _normalize_query("aapl") == "aapl"
