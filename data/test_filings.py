from data.sec_api import get_company_submissions
from data.filings import (
    get_filing_document,
    extract_filing_text,
    extract_formatted_sections,
    extract_accounting_topics,
    analyze_accounting_topic
)


cik = "320193"

submissions = get_company_submissions(cik)

recent = submissions["filings"]["recent"]

accession_number = None
primary_document = None

for i, form in enumerate(recent["form"]):
    if form == "10-K":
        accession_number = recent["accessionNumber"][i]
        primary_document = recent["primaryDocument"][i]
        filing_date = recent["filingDate"][i]
        report_date = recent["reportDate"][i]
        break

if accession_number is None:
    raise ValueError("No 10-K filing found.")

print("10-K FOUND")
print("========================================")
print("Accession:", accession_number)
print("Filing Date:", filing_date)
print("Report Date:", report_date)
print("Primary Document:", primary_document)

html = get_filing_document(
    cik,
    accession_number,
    primary_document
)

print()
print("RAW HTML")
print("========================================")
print("Characters:", len(html))

text = extract_filing_text(html)

print()
print("CLEANED FILING TEXT")
print("========================================")
print("Characters:", len(text))

sections = extract_formatted_sections(html)

critical_estimates = sections[
    "critical_accounting_estimates"
]

print()
print("CRITICAL_ACCOUNTING_ESTIMATES")
print("========================================")
print("Characters:", len(critical_estimates))
print()
print(critical_estimates)

topics = extract_accounting_topics(
    critical_estimates
)

print()
print("ACCOUNTING TOPICS")
print("========================================")

for topic, topic_text in topics.items():
    print()
    print(topic)
    print("----------------------------------------")
    print(topic_text)

print()
print("ACCOUNTING RISK EVIDENCE")
print("========================================")

for topic, topic_text in topics.items():
    analysis = analyze_accounting_topic(topic_text)

    print()
    print(topic)
    print("----------------------------------------")
    print("Judgment:", analysis["judgment"])
    print("Uncertainty:", analysis["uncertainty"])
    print("Material Impact:", analysis["material_impact"])
    print("Evidence:", analysis["evidence"])