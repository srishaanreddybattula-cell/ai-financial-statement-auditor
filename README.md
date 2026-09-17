# AI Financial Statement Auditor

SEC-grounded AI financial statement analysis and financial reporting risk assessment platform.

## What it does

This project analyzes publicly available SEC filing and XBRL data to surface financial reporting indicators that may deserve additional review. It is designed as a screening and research tool, not as an audit opinion, fraud detector, or investment recommendation.

The application currently provides:

- Financial reporting risk score from 0 to 100
- Prototype risk category
- Key financial findings and supporting evidence
- Data quality and core-metric coverage checks
- SEC XBRL provenance, including filing form, filing date, accession number, and period end
- Direct link to the source SEC filing
- Goodwill screening with protection against stale historical facts being treated as current data
- Revenue, net income, and operating cash flow trends
- Historical revenue-growth anomaly review
- Working-capital, cash-flow, accrual, and liquidity signals
- Accounting policy and critical-estimate keyword review
- Peer comparison using metric-specific risk direction and robust deviation measures
- Downloadable PDF and Excel screening reports
- Company lookup by ticker or company name, with case-insensitive matching
- Support for SEC-reporting foreign issuers and annual forms including 10-K, 20-F, and 40-F, where the SEC provides the required XBRL facts
- IFRS-aware financial fact mapping for common metrics used by foreign private issuers

## Supported company lookup

The company field accepts a ticker or company name, regardless of capitalization. Examples include:

```text
Apple
APPLE
apple
ApPlE
AAPL
Microsoft
ASML
Alibaba
Toyota
Sony
```

The lookup is driven by SEC issuer data rather than a small hard-coded company list. Coverage therefore depends on whether the company is an SEC-reporting issuer with usable EDGAR data. Foreign companies are supported when their SEC filings and XBRL facts are available.

## Architecture

```text
SEC submissions + SEC company facts
                |
                v
        Company lookup layer
       name / ticker / CIK
                |
                v
        Data extraction layer
                |
                v
       Annual normalization
     US-GAAP + IFRS concepts
                |
                v
        Analysis pipeline
       /       |        \
 financial  accounting   peer
 signals     review     comparison
       \       |        /
                v
          Risk assessment
                |
                v
        Streamlit dashboard
                |
          PDF / Excel reports
```

## Main technology

- Python
- Streamlit
- SEC submissions and XBRL company facts
- pandas
- pytest
- ReportLab
- openpyxl
- GitHub Actions

## Running locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
python -m streamlit run app.py
```

Then open the local Streamlit address shown in the terminal, enter a ticker or company name such as `AAPL`, `Apple`, or `ASML`, and select **Analyze company**.

## Testing

Run the automated test suite with:

```bash
pytest -q
```

GitHub Actions also runs Python compilation and the full test suite on pushes to the repository.

## Important limitations

- Results depend on the availability and structure of SEC XBRL facts.
- Global coverage means SEC-reporting companies with available EDGAR data; it does not mean every company worldwide files with the SEC.
- Some foreign issuers use IFRS concepts, while others may have different available XBRL structures, so metric coverage can vary by issuer.
- The model uses prototype screening thresholds and is not an audit procedure.
- A flagged signal does not establish fraud, an accounting error, or a material misstatement.
- Peer comparisons are limited to configured peer groups and comparable annual data.
- Historical or missing facts are not automatically evidence of a reporting problem.
- Users should review the underlying SEC filing before drawing accounting conclusions.

<!-- Automated regression fixture updated with the annual-period selection fix. -->
