import requests

SEC_HEADERS = {
    "User-Agent": "AI Financial Statement Auditor srishaanreddybattula@gmail.com"
}
SEC_COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"


def get_sec_companies():
    response = requests.get(
        SEC_COMPANY_TICKERS_URL,
        headers=SEC_HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    return response.json().values()


def find_company(query):
    """Find an SEC-reporting company by ticker or company name."""
    query = query.strip().lower()
    if not query:
        return None

    companies = list(get_sec_companies())

    # Prefer an exact ticker match.
    for company in companies:
        if str(company.get("ticker", "")).strip().lower() == query:
            return company

    # Then prefer an exact company-name match.
    for company in companies:
        if str(company.get("title", "")).strip().lower() == query:
            return company

    # Finally allow a company-name search.
    matches = [
        company
        for company in companies
        if query in str(company.get("title", "")).strip().lower()
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
    }
