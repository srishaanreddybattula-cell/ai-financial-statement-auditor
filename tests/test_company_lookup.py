from data.ticker_map import _base_company_name, _is_corporate_name_match


def test_common_global_company_names_normalize_cleanly():
    assert _base_company_name("Apple Inc.") == "apple"
    assert _base_company_name("Microsoft Corporation") == "microsoft"
    assert _base_company_name("NVIDIA Corporation") == "nvidia"
    assert _base_company_name("Alphabet Inc.") == "alphabet"


def test_simple_name_matches_legal_suffix():
    assert _is_corporate_name_match("Apple", "Apple Inc.")
    assert _is_corporate_name_match("Microsoft", "Microsoft Corporation")
    assert _is_corporate_name_match("NVIDIA", "NVIDIA Corporation")


def test_simple_name_does_not_match_unrelated_issuer_with_same_prefix():
    assert not _is_corporate_name_match("Apple", "Apple Hospitality REIT, Inc.")
