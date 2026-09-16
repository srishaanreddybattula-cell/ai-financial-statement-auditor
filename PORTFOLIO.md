# AI Financial Statement Auditor

## Project Overview

AI Financial Statement Auditor is an SEC-grounded financial reporting risk screening platform. It uses publicly available SEC submissions and XBRL company facts to organize financial data, calculate screening signals, compare selected metrics with peers, review accounting-policy topics, and produce PDF and Excel reports.

## Why I Built It

The project explores how financial analysis workflows can be made more systematic and evidence-grounded with software. Instead of treating an AI-generated answer as the source of truth, the application keeps the analysis connected to SEC filing data and exposes filing provenance so users can trace results back to the underlying filing.

## Technical Highlights

- Python and Streamlit application architecture
- SEC submissions and XBRL company-facts data extraction
- Annual financial-data normalization
- Financial reporting risk signals across multiple dimensions
- Robust peer-deviation analysis with metric-specific risk direction
- Accounting policy and critical-estimate keyword review
- SEC filing provenance and direct source-filing links
- Data-quality and screening-readiness checks
- Protection against stale historical goodwill facts being treated as current
- Automated regression tests with pytest
- GitHub Actions CI for compilation and tests
- PDF reports generated with ReportLab
- Excel reports generated with openpyxl

## Key Engineering Decisions

### SEC-grounded provenance

The application preserves filing metadata such as form, filing date, accession number, period dates, and SEC source URLs. This makes the screening output more traceable than a system that only presents calculated numbers.

### Screening, not diagnosis

Risk values are explicitly treated as screening signals. A flagged indicator does not establish fraud, an accounting error, or a material misstatement. Users are directed to review the underlying SEC filing before drawing conclusions.

### Data-quality protection

The system checks core metric coverage and annual history before treating the dataset as ready for screening. Historical facts are not automatically treated as current evidence.

## Example Workflow

1. User enters a public-company ticker.
2. The application retrieves SEC data.
3. Financial facts are normalized into annual series.
4. Financial, accounting-policy, cash-flow, working-capital, liquidity, goodwill, and peer signals are calculated.
5. Risk dimensions are combined into a 0–100 prototype screening score.
6. The dashboard shows evidence and SEC provenance.
7. The user can export PDF and Excel screening reports.

## Testing

The repository includes automated regression tests and a GitHub Actions workflow that compiles the project and runs the test suite.

## Limitations

This is a prototype screening and research system. Its results depend on the availability and structure of SEC XBRL data, configured peer groups, and prototype thresholds. It is not an audit procedure, audit opinion, fraud detector, or investment recommendation.
