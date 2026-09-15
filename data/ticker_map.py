import requests

SEC_HEADERS = {
    "User-Agent": "AI Financial Statement Auditor srishaanreddybattula@gmail.com"
}


def get_cik_from_ticker(ticker):
    url = "https://www.sec.gov/files/company_tickers.json"

    response = requests.get(
        url,
        headers=SEC_HEADERS,
        timeout=30
    )

    response.raise_for_status()

    companies = response.json()

    ticker = ticker.upper().strip()

    for company in companies.values():
        if company["ticker"] == ticker:
            return str(company["cik_str"]).zfill(10)

    return None