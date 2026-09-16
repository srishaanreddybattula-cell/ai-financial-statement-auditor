from data.ticker_map import (
    _base_company_name,
    _is_corporate_name_match,
    _normalize_query,
)


def test_common_global_company_names_normalize_cleanly():
    assert _base_company_name("Apple Inc.") == "apple"
    assert _base_company_name("Microsoft Corporation") == "microsoft"
    assert _base_company_name("NVIDIA Corporation") == "nvidia"
    assert _base_company_name("Alphabet Inc.") == "alphabet"
    assert _base_company_name("Alibaba Group Holding Limited") == "alibaba"
    assert _base_company_name("ASML Holding N.V.") == "asml"
    assert _base_company_name("Sony Group Corporation") == "sony"
    assert _base_company_name("Toyota Motor Corporation") == "toyota motor"


def test_input_matching_is_case_insensitive():
    assert _normalize_query("APPLE") == _normalize_query("Apple")
    assert _normalize_query("apple") == _normalize_query("Apple")
    assert _normalize_query("ApPlE") == _normalize_query("Apple")
    assert _normalize_query("AAPL") == _normalize_query("aapl")
    assert _normalize_query("ApPlE, Inc.") == "apple inc"


def test_simple_name_matches_legal_suffix():
    assert _is_corporate_name_match("Apple", "Apple Inc.")
    assert _is_corporate_name_match("Microsoft", "Microsoft Corporation")
    assert _is_corporate_name_match("NVIDIA", "NVIDIA Corporation")
    assert _is_corporate_name_match("Alibaba", "Alibaba Group Holding Limited")
    assert _is_corporate_name_match("ASML", "ASML Holding N.V.")
    assert _is_corporate_name_match("Sony", "Sony Group Corporation")
    assert _is_corporate_name_match("Alibaba Group Holding", "Alibaba Group Holding Limited")
    assert _is_corporate_name_match("Toyota Motor", "Toyota Motor Corporation")
    assert _is_corporate_name_match("Toyota", "Toyota Motor Corporation")
    assert _is_corporate_name_match("Toyota", "Toyota Motor Corp")


def test_simple_name_does_not_match_unrelated_issuer_with_same_prefix():
    assert not _is_corporate_name_match("Apple", "Apple Hospitality REIT, Inc.")
    assert not _is_corporate_name_match("Microsoft", "Microsoft 365 Holdings Inc.")
    assert not _is_corporate_name_match("Toyota", "Toyota Industries Corporation")
    assert not _is_corporate_name_match("Technology", "Technology Partners Inc.")
