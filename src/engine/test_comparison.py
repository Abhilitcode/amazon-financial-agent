
from models import FinancialProfile, FinancialEvent, FinancialScenario
from comparison import compare_scenarios

# 1. Create the user's financial profile
profile = FinancialProfile(
    monthly_salary=80000,
    other_income=5000,
    current_savings=150000,
    fixed_expenses={
        "rent": 20000,
        "loan_emi": 15000,
        "insurance": 3000,
    },
    essential_expenses={
        "groceries": 8000,
        "transport": 4000,
        "utilities": 3000,
    },
    flexible_expenses={
        "shopping": 3000,
        "dining": 4000,
        "entertainment": 2000,
    },
    monthly_savings_goal=15000,
    minimum_buffer=30000,
)

# 2. Scenario A: No new financial commitment
baseline = FinancialScenario(
    name="Baseline",
    events=[],
)

# 3. Scenario B: Buy a car
car_emi = FinancialEvent(
    name="Car EMI",
    event_type="recurring_expense",
    amount=20000,
    start_month=1,
    duration_months=60,
)

car_scenario = FinancialScenario(
    name="Buy a car",
    events=[car_emi],
)

# 4. Compare the scenarios for three months
comparison = compare_scenarios(
    profile,
    baseline,
    car_scenario,
    months=3,
)

# 5. Display the results
print("Scenario A:", comparison["scenario_a"])
print("Scenario B:", comparison["scenario_b"])
print(
    "Final savings difference:",
    comparison["ending_savings_difference"],
)

print("\nMonth-by-month comparison:")
for month in comparison["monthly_comparison"]:
    print(month)
