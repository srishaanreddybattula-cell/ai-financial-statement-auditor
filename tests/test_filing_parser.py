from data.filings import analyze_accounting_topic, extract_accounting_topics


def test_extract_accounting_topics_returns_all_matches():
    text = (
        "Revenue Recognition details. "
        "Goodwill details. "
        "Leases details."
    )

    topics = extract_accounting_topics(text)

    assert list(topics) == [
        "Revenue Recognition",
        "Goodwill",
        "Leases",
    ]
    assert topics["Revenue Recognition"] == "Revenue Recognition details."
    assert topics["Goodwill"] == "Goodwill details."
    assert topics["Leases"] == "Leases details."


def test_extract_accounting_topics_handles_no_matches():
    assert extract_accounting_topics("No accounting topic headings here.") == {}


def test_analyze_accounting_topic_detects_review_evidence():
    result = analyze_accounting_topic(
        "This estimate requires significant judgment and may have a material impact."
    )

    assert result["judgment"] is True
    assert result["material_impact"] is True
    assert "significant judgment" in result["evidence"]
    assert "material impact" in result["evidence"]
