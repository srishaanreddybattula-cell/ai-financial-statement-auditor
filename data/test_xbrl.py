from xbrl import get_company_facts

company_facts = get_company_facts("320193")

us_gaap = company_facts["facts"]["us-gaap"]

for tag in ["LongTermDebtCurrent", "LongTermDebtNoncurrent"]:
    print("\n" + tag)
    print("==============================")

    try:
        fact = us_gaap[tag]

        for unit, values in fact["units"].items():
            for value in values[-15:]:
                if value.get("form") == "10-K":
                    print(value)

    except KeyError:
        print("Tag not found")