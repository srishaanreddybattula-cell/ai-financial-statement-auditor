from data.ticker_map import _normalize_query


def test_documented_company_input_examples_normalize():
    examples = {
        "Apple": "apple",
        "APPLE": "apple",
        "apple": "apple",
        "ApPlE": "apple",
        "AAPL": "aapl",
        "ASML": "asml",
        "Alibaba": "alibaba",
        "Toyota": "toyota",
        "Sony": "sony",
    }
    for raw, expected in examples.items():
        assert _normalize_query(raw) == expected
