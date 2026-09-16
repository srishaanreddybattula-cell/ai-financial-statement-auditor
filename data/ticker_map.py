import re
import requests

SEC_HEADERS = {
    "User-Agent": "AI Financial Statement Auditor srishaanreddybattula@gmail.com"
}
SEC_COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_COMPANY_TICKERS_EXCHANGE_URL = "https://www.sec.gov/files/company_tickers_exchange.json"


def _normalize_query(value):
    """Normalize user input so capitalization and punctuation do not matter."""
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").strip().lower()).strip()


def get_sec_companies():
    """Return SEC-reporting issuers from SEC's ticker/CIK datasets."""
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


def find_company(query):
    """Find an SEC issuer by ticker or company name.

    Matching is case-insensitive and ignores punctuation/spacing differences.
    Exact ticker matches always win, so inputs such as AAPL, aapl, Apple, and
    APPLE can resolve to Apple's SEC issuer when present in the SEC dataset.
    """
    normalized_query = _normalize_query(query)
    if not normalized_query:
        return None

    companies = list(get_sec_companies())

    # 1. Exact ticker match. This is intentionally checked before company names.
    ticker_matches = [
        company
        for company in companies
        if _normalize_query(company.get("ticker")) == normalized_query
    ]
    if ticker_matches:
        # Prefer an exchange-listed security with a valid CIK.
        ticker_matches = [c for c in ticker_matches if c.get("cik_str")]
        if ticker_matches:
            return ticker_matches[0]

    # 2. Exact company-name match.
    name_matches = [
        company
        for company in companies
        if _normalize_query(company.get("title")) == normalized_query
    ]
    if len(name_matches) == 1:
        return name_matches[0]

    # 3. Unique company-name containment match.
    matches = [
        company
        for company in companies
        if normalized_query in _normalize_query(company.get("title"))
    ]
    if len(matches) == 1:
        return matches[0]

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
