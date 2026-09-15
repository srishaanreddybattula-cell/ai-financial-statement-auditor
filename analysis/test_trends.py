from analysis.trends import calculate_year_over_year
from analysis.trends import calculate_multi_year_trend


test_data = [
    {"year": 2021, "value": 100},
    {"year": 2022, "value": 120},
    {"year": 2023, "value": 150},
]


year_over_year = calculate_year_over_year(test_data)
multi_year = calculate_multi_year_trend(test_data)


print("YEAR-OVER-YEAR")
print("==============================")
print(year_over_year)

print("\nMULTI-YEAR TREND")
print("==============================")
print(multi_year)
