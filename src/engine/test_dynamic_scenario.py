
from models import FinancialProfile, FinancialEvent, FinancialScenario
from simulation import simulate_scenario
from calculations import calculate_total_expenses


# 1. Create a profile
profile = FinancialProfile(
    monthly_salary=80000,
    other_income=5000,
    current_savings=150000,
    fixed_expenses={"rent": 20000},
    essential_expenses={"groceries": 8000},
    flexible_expenses={"dining": 4000},
    monthly_savings_goal=15000,
    minimum_buffer=30000,
)

# 2. Dynamically add a new expense
profile.add_expense("Pet care", 2500, "flexible")

print("Flexible expenses:", profile.flexible_expenses)
print("Total regular expenses:", calculate_total_expenses(profile))


# 3. Create an event targeting the new expense
pet_care_increase = FinancialEvent(
    name="Pet care cost increase",
    event_type="expense_percentage_change",
    percentage=20,
    target_expense="Pet care",
    start_month=2,
    duration_months=2,
)

scenario = FinancialScenario(
    name="Pet care stress test",
    events=[pet_care_increase],
)


# 4. Run a four-month simulation
results = simulate_scenario(profile, scenario, months=4)

for result in results:
    print(
        f"Month {result.month} | "
        f"Regular expenses: ₹{result.regular_expenses:,.0f} | "
        f"Scenario expenses: ₹{result.scenario_expenses:,.0f} | "
        f"Ending savings: ₹{result.ending_savings:,.0f}"
    )
