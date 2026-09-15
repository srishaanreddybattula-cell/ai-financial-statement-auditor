from ticker_map import get_cik_from_ticker

ticker = "AAPL"

cik = get_cik_from_ticker(ticker)

print("Ticker:", ticker)
print("CIK:", cik)