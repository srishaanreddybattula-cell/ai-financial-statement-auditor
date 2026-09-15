POLICY_KEYWORDS = {
    "revenue_recognition": [
        "revenue recognition",
        "revenue is recognized",
        "performance obligations",
        "contract liabilities",
        "deferred revenue"
    ],
    "inventory": [
        "inventory",
        "inventories",
        "cost of sales",
        "lower of cost",
        "net realizable value"
    ],
    "depreciation": [
        "depreciation",
        "property, plant and equipment",
        "useful lives"
    ],
    "amortization": [
        "amortization",
        "finite-lived intangible",
        "useful life"
    ],
    "goodwill": [
        "goodwill",
        "goodwill impairment",
        "reporting unit"
    ],
    "stock_based_compensation": [
        "stock-based compensation",
        "share-based compensation",
        "stock compensation",
        "restricted stock units"
    ],
    "leases": [
        "leases",
        "lease liabilities",
        "right-of-use assets",
        "operating leases",
        "finance leases"
    ],
    "income_taxes": [
        "income taxes",
        "deferred tax",
        "effective tax rate",
        "uncertain tax positions"
    ],
    "fair_value": [
        "fair value",
        "fair value measurements",
        "level 1",
        "level 2",
        "level 3"
    ],
    "impairments": [
        "impairment",
        "impairment charges",
        "recoverability"
    ],
    "acquisitions": [
        "business combinations",
        "acquisition",
        "acquisitions",
        "purchase price allocation"
    ],
    "related_parties": [
        "related parties",
        "related party transactions"
    ]
}


def find_policy_keywords(text):
    if not text:
        return {}

    text_lower = text.lower()
    results = {}

    for policy, keywords in POLICY_KEYWORDS.items():
        matches = []

        for keyword in keywords:
            if keyword in text_lower:
                matches.append(keyword)

        results[policy] = matches

    return results


def get_policy_flags(text):
    matches = find_policy_keywords(text)

    flags = {}

    for policy, keywords in matches.items():
        flags[policy] = len(keywords) > 0

    return flags


def calculate_policy_risk(policy_flags):
    risk_score = 0

    risk_weights = {
        "revenue_recognition": 25,
        "inventory": 5,
        "depreciation": 5,
        "amortization": 5,
        "goodwill": 10,
        "stock_based_compensation": 10,
        "leases": 5,
        "income_taxes": 5,
        "fair_value": 10,
        "impairments": 10,
        "acquisitions": 5,
        "related_parties": 5
    }

    for policy, flagged in policy_flags.items():
        if flagged:
            risk_score += risk_weights.get(policy, 0)

    return min(risk_score, 100)


def analyze_accounting_policies(text):
    policy_matches = find_policy_keywords(text)
    policy_flags = get_policy_flags(text)
    risk_score = calculate_policy_risk(policy_flags)

    return {
        "policy_matches": policy_matches,
        "policy_flags": policy_flags,
        "risk_score": risk_score
    }