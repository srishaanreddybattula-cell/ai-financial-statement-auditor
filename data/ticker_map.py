from functools import lru_cache
import re

import requests

SEC_HEADERS = {
    "User-Agent": "AI Financial Statement Auditor srishaanreddybattula@gmail.com"
}
SEC_COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_COMPANY_TICKERS_EXCHANGE_URL = "https://www.sec.gov/files/company_tickers_exchange.json"
SEC_CIK_LOOKUP_URL = "https://www.sec.gov/Archives/edgar/cik-lookup-data.txt"


LEGAL_SUFFIXES = {
    "inc", "incorporated", "corp", "corporation", "co", "company",
    "ltd", "limited", "plc", "sa", "ag", "nv", "se", "spa", "sarl",
    "pte", "llc", "lp", "llp",
}
COMPOUND_LEGAL_SUFFIXES = {
    ("n", "v"), ("p", "l", "c"), ("s", "a"), ("a", "g"),
}
NAME_DESCRIPTORS = {"group", "holding", "holdings"}


def _normalize_query(value):
    """Normalize user input so capitalization and punctuation do not matter."""
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").strip().lower()).strip()


def _base_company_name(value):
    """Return a normalized name with trailing legal suffixes/descriptors removed."""
    words = _normalize_query(value).split()
    while len(words) > 1:
        if words[-1] in LEGAL_SUFFIXES:
            words.pop()
            continue
        removed_compound = False
        for suffix in COMPOUND_LEGAL_SUFFIXES:
            if len(words) > len(suffix) and tuple(words[-len(suffix):]) == suffix:
                del words[-len(suffix):]
                removed_compound = True
                break
        if not removed_compound:
            break

    # International issuers often use descriptors between the core name and
    # the legal suffix, e.g. Alibaba Group Holding Limited. Strip only known
    # descriptors at the end so unrelated names such as Apple Hospitality REIT
    # remain distinct.
    while len(words) > 1 and words[-1] in NAME_DESCRIPTORS:
        words.pop()

    return " ".join(words)


@lru_cache(maxsize=1)
def get_sec_companies():
    """Return SEC ticker/exchange associations, including foreign issuers."""
    response = requests.get(
        SEC_COMPANY_TICKERS_EXCHANGE_URL,
        headers=SEC_HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()

    fields = payload.get("fields", [])
    companies = []
    for row in payload.get("data", []):
        record = dict(zip(fields, row))
        companies.append(
            {
                "cik_str": record.get("cik"),
                "ticker": record.get("ticker", ""),
                "title": record.get("name", ""),
                "exchange": record.get("exchange", ""),
            }
        )

    if companies:
        return companies

    fallback = requests.get(
        SEC_COMPANY_TICKERS_URL,
        headers=SEC_HEADERS,
        timeout=30,
    )
    fallback.raise_for_status()
    return list(fallback.json().values())


@lru_cache(maxsize=1)
def get_sec_cik_names():
    """Load SEC's broader CIK/name file for issuers without ticker mappings."""
    response = requests.get(
        SEC_CIK_LOOKUP_URL,
        headers=SEC_HEADERS,
        timeout=60,
    )
    response.raise_for_status()

    companies = []
    for line in response.text.splitlines():
        parts = line.strip().split("|")
        if len(parts) < 2:
            continue
        name, cik = parts[0].strip(), parts[1].strip()
        if name and cik.isdigit():
            companies.append(
                {
                    "cik_str": int(cik),
                    "ticker": "",
                    "title": name,
                    "exchange": "",
                }
            )
    return companies


def _dedupe_companies(companies):
    """Deduplicate aliases so one issuer is never treated as multiple matches."""
    unique = {}
    for company in companies:
        cik = str(company.get("cik_str", "")).zfill(10)
        if cik:
            unique[cik] = company
    return list(unique.values())


def _is_corporate_name_match(query, title):
    """Recognize a short name such as 'Apple' -> 'Apple Inc.'."""
    query_words = _normalize_query(query).split()
    title_words = _normalize_query(title).split()
    if not query_words or len(title_words) <= len(query_words):
        return False
    if title_words[:len(query_words)] != query_words:
        return False

    normalized_query = _normalize_query(query)
    if _base_company_name(title) == normalized_query:
        return True

    remaining = title_words[len(query_words):]
    if all(word in LEGAL_SUFFIXES for word in remaining):
        return True
    if any(tuple(remaining) == suffix for suffix in COMPOUND_LEGAL_SUFFIXES):
        return True

    if remaining and all(word in NAME_DESCRIPTORS or word in LEGAL_SUFFIXES for word in remaining):
        return True
    return False


def find_company(query):
    """Find an SEC-reporting issuer by ticker or company name.

    Matching is case-insensitive and ignores punctuation/spacing differences.
    Exact ticker matches are preferred, followed by exact legal/base company-name
    matches and then carefully limited partial matches. The broader SEC CIK/name
    database is used as a fallback for filers without ticker associations.
    """
    normalized_query = _normalize_query(query)
    if not normalized_query:
        return None

    companies = _dedupe_companies(get_sec_companies())

    ticker_matches = [
        company for company in companies
        if _normalize_query(company.get("ticker")) == normalized_query
    ]
    if ticker_matches:
        return ticker_matches[0]

    name_matches = [
        company for company in companies
        if _normalize_query(company.get("title")) == normalized_query
    ]
    if len(name_matches) == 1:
        return name_matches[0]
    if len(name_matches) > 1:
        unique = _dedupe_companies(name_matches)
        if len(unique) == 1:
            return unique[0]

    base_matches = _dedupe_companies([
        company for company in companies
        if _base_company_name(company.get("title")) == normalized_query
    ])
    if len(base_matches) == 1:
        return base_matches[0]

    corporate_matches = _dedupe_companies([
        company for company in companies
        if _is_corporate_name_match(normalized_query, company.get("title", ""))
    ])
    if len(corporate_matches) == 1:
        return corporate_matches[0]

    partial_matches = _dedupe_companies([
        company for company in companies
        if normalized_query in _normalize_query(company.get("title"))
    ])
    if len(partial_matches) == 1:
        return partial_matches[0]

    cik_companies = _dedupe_companies(get_sec_cik_names())

    fallback_exact = [
        company for company in cik_companies
        if _normalize_query(company.get("title")) == normalized_query
    ]
    if len(fallback_exact) == 1:
        return fallback_exact[0]

    fallback_base = _dedupe_companies([
        company for company in cik_companies
        if _base_company_name(company.get("title")) == normalized_query
    ])
    if len(fallback_base) == 1:
        return fallback_base[0]

    fallback_corporate = _dedupe_companies([
        company for company in cik_companies
        if _is_corporate_name_match(normalized_query, company.get("title", ""))
    ])
    if len(fallback_corporate) == 1:
        return fallback_corporate[0]

    fallback_partial = _dedupe_companies([
        company for company in cik_companies
        if normalized_query in _normalize_query(company.get("title"))
    ])
    if len(fallback_partial) == 1:
        return fallback_partial[0]

    return None


def get_cik_from_ticker(ticker):
    company = find_company(ticker)
    if company is None:
        return None
    return str(company["cik_str"]).zfill(10)


def get_company_from_query(query):
    company = find_company(query)
    if company is None:
        return None
    return {
        "cik": str(company["cik_str"]).zfill(10),
        "ticker": str(company.get("ticker", "")).strip().upper(),
        "name": str(company.get("title", "")).strip(),
        "exchange": str(company.get("exchange", "")).strip(),
    }
