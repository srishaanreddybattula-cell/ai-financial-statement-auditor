import streamlit as st

from data.ticker_map import get_cik_from_ticker
from data.sec_api import get_company_submissions


st.title("AI Financial Statement Auditor")

st.write("Enter a public company ticker to retrieve its SEC information.")

ticker = st.text_input("Enter a company ticker:")


if ticker:
    ticker = ticker.upper().strip()

    with st.spinner("Connecting to the SEC..."):

        try:
            cik = get_cik_from_ticker(ticker)

            if cik is None:
                st.error(f"Could not find a company with ticker: {ticker}")

            else:
                company = get_company_submissions(cik)

                st.success("SEC data retrieved successfully!")

                st.subheader(company["name"])

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Ticker:**", ticker)

                with col2:
                    st.write("**CIK:**", cik)

                st.write(
                    "Recent SEC filings:",
                    len(company["filings"]["recent"]["form"])
                )

        except Exception as e:
            st.error(f"Something went wrong: {e}")