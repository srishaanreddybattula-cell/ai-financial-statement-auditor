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
    """Return SEC-reporting issuers from SEC's ticker/CIK datasets.

    The exchange dataset includes many foreign issuers and ADRs in addition to
    U.S. companies. The regular ticker dataset is retained as a fallback.
    """
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
    """Find an SEC-reporting issuer by ticker or company name.

    Matching is case-insensitive and ignores punctuation, spacing differences,
    and common formatting differences. This supports inputs such as Apple,
    APPLE, apple, and AAPL.
    """
    normalized_query = _normalize_query(query)
    if not normalized_query:
        return None

    companies = list(get_sec_companies())

    # Prefer an exact ticker match, regardless of capitalization.
    for company in companies:
        if _normalize_query(company.get("ticker")) == normalized_query:
            return company

    # Then prefer an exact company-name match.
    for company in companies:
        if _normalize_query(company.get("title")) == normalized_query:
            return company

    # Finally allow a company-name search. Only return an unambiguous match.
    matches = [
        company
        for company in companies
        if normalized_query in _normalize_query(company.get("title"))
    ]

    return matches[0] if len(matches) == 1 else None


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
