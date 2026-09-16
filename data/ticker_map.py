from functools import lru_cache
import re

import requests

SEC_HEADERS = {
    "User-Agent": "AI Financial Statement Auditor srishaanreddybattula@gmail.com"
}
SEC_COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_COMPANY_TICKERS_EXCHANGE_URL = "https://www.sec.gov/files/company_tickers_exchange.json"
SEC_CIK_LOOKUP_URL = "https://www.sec.gov/Archives/edgar/cik-lookup-data.txt"


def _normalize_query(value):
    """Normalize user input so capitalization and punctuation do not matter."""
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").strip().lower()).strip()


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


def find_company(query):
    """Find an SEC-reporting issuer by ticker or company name.

    Matching is case-insensitive and ignores punctuation/spacing differences.
    Exact ticker matches are preferred, followed by exact company-name matches,
    then unique partial company-name matches. If the ticker dataset cannot
    identify a name, SEC's broader CIK/name database is used as a fallback.
    """
    normalized_query = _normalize_query(query)
    if not normalized_query:
        return None

    companies = _dedupe_companies(get_sec_companies())

    # Exact ticker always wins. This fixes inputs such as AAPL, aapl, or Aapl.
    ticker_matches = [
        company
        for company in companies
        if _normalize_query(company.get("ticker")) == normalized_query
    ]
    if ticker_matches:
        return ticker_matches[0]

    # Exact company name, case-insensitive. This supports Apple, APPLE, etc.
    name_matches = [
        company
        for company in companies
        if _normalize_query(company.get("title")) == normalized_query
    ]
    if len(name_matches) == 1:
        return name_matches[0]
    if len(name_matches) > 1:
        # Same issuer may have multiple security aliases. Collapse by CIK.
        unique = _dedupe_companies(name_matches)
        if len(unique) == 1:
            return unique[0]

    # Unique partial name match from ticker/exchange associations.
    partial_matches = _dedupe_companies([
        company
        for company in companies
        if normalized_query in _normalize_query(company.get("title"))
    ])
    if len(partial_matches) == 1:
        return partial_matches[0]

    # Broader SEC CIK/name fallback for filers without a ticker/exchange entry.
    cik_companies = _dedupe_companies(get_sec_cik_names())
    fallback_exact = [
        company
        for company in cik_companies
        if _normalize_query(company.get("title")) == normalized_query
    ]
    if len(fallback_exact) == 1:
        return fallback_exact[0]

    fallback_partial = [
        company
        for company in cik_companies
        if normalized_query in _normalize_query(company.get("title"))
    ]
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
