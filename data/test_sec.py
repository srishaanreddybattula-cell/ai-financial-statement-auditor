from sec_api import get_company_submissions

apple = get_company_submissions("320193")

print("Company:", apple["name"])
print("CIK:", apple["cik"])
print("Recent filings:", len(apple["filings"]["recent"]["form"]))