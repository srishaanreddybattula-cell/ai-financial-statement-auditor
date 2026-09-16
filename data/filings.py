import requests
from bs4 import BeautifulSoup


SEC_HEADERS = {
    "User-Agent": "AI Financial Statement Auditor srishaanreddybattula@gmail.com"
}


def get_filing_document(cik, accession_number, primary_document):
    cik = str(cik).zfill(10)
    accession_number = accession_number.replace("-", "")

    url = (
        f"https://www.sec.gov/Archives/edgar/data/"
        f"{int(cik)}/{accession_number}/{primary_document}"
    )

    response = requests.get(
        url,
        headers=SEC_HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.text


def extract_filing_text(html):
    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    for element in soup(["script", "style", "ix:header"]):
        element.decompose()

    text = soup.get_text(
        separator=" ",
        strip=True
    )

    return text


def extract_section(text, start_keyword, end_keywords):
    if not text:
        return ""

    start_position = text.lower().find(
        start_keyword.lower()
    )

    if start_position == -1:
        return ""

    end_position = len(text)

    for keyword in end_keywords:
        position = text.lower().find(
            keyword.lower(),
            start_position + len(start_keyword)
        )

        if position != -1 and position < end_position:
            end_position = position

    return text[start_position:end_position]


def extract_formatted_sections(html):
    sections = {}

    start_position = html.lower().find(
        "critical accounting estimates"
    )

    if start_position == -1:
        sections["critical_accounting_estimates"] = ""
        return sections

    end_position = html.lower().find(
        "legal and other contingencies",
        start_position
    )

    if end_position == -1:
        end_position = html.lower().find(
            "item 7a.",
            start_position
        )

    if end_position == -1:
        end_position = len(html)

    section_html = html[start_position:end_position]

    soup = BeautifulSoup(
        section_html,
        "html.parser"
    )

    text = soup.get_text(
        separator=" ",
        strip=True
    )

    text = " ".join(text.split())

    sections["critical_accounting_estimates"] = text

    return sections


def extract_accounting_topics(text):
    topics = {}

    topic_headers = [
        "Uncertain Tax Positions",
        "Revenue Recognition",
        "Goodwill",
        "Stock-Based Compensation",
        "Leases",
        "Fair Value Measurements",
        "Impairments",
    ]

    if not text:
        return topics

    text_lower = text.lower()
    positions = []

    for header in topic_headers:
        position = text_lower.find(header.lower())
        if position != -1:
            positions.append((position, header))

    positions.sort()

    for i, (start_position, header) in enumerate(positions):
        if i + 1 < len(positions):
            end_position = positions[i + 1][0]
        else:
            end_position = len(text)

        topic_text = text[start_position:end_position].strip()
        topics[header] = topic_text

    return topics


def analyze_accounting_topic(text):
    if not text:
        return {
            "judgment": False,
            "uncertainty": False,
            "material_impact": False,
            "evidence": [],
        }

    text_lower = text.lower()
    evidence = []

    judgment_keywords = [
        "significant judgment",
        "management's expectations",
        "requires management",
        "requires significant judgment",
    ]

    uncertainty_keywords = [
        "uncertain",
        "uncertainties",
        "no assurance",
        "final outcome",
    ]

    material_impact_keywords = [
        "material impact",
        "materially affect",
        "material effect",
    ]

    judgment = False
    uncertainty = False
    material_impact = False

    for keyword in judgment_keywords:
        if keyword in text_lower:
            judgment = True
            evidence.append(keyword)

    for keyword in uncertainty_keywords:
        if keyword in text_lower:
            uncertainty = True
            evidence.append(keyword)

    for keyword in material_impact_keywords:
        if keyword in text_lower:
            material_impact = True
            evidence.append(keyword)

    return {
        "judgment": judgment,
        "uncertainty": uncertainty,
        "material_impact": material_impact,
        "evidence": evidence,
    }
