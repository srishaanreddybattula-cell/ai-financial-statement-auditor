from xbrl import get_company_facts
from financial_data import get_debt

company_facts = get_company_facts("320193")

debt = get_debt(company_facts)

print("DEBT DATA")
print("==============================")

for item in debt[-10:]:
    print(item)