from models import FinancialProfile, FinancialEvent, FinancialScenario
from comparison import compare_multiple_scenarios

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

car_emi = FinancialEvent(
    name="Car EMI",
    event_type="recurring_expense",
    amount=20000,
    start_month=1,
    duration_months=60,
)

vacation = FinancialEvent(
    name="Vacation",
    event_type="one_time_expense",
    amount=60000,
    start_month=2,
)

salary_cut = FinancialEvent(
    name="Salary reduction",
    event_type="income_percentage_change",
    percentage=-15,
    start_month=2,
    duration_months=2,
)

scenario_a = FinancialScenario(
    name="Car",
    events=[car_emi],
)

scenario_ab = FinancialScenario(
    name="Car + vacation",
    events=[car_emi, vacation],
)

scenario_abc = FinancialScenario(
    name="Car + vacation + salary cut",
    events=[car_emi, vacation, salary_cut],
)

scenarios = [scenario_a, scenario_ab, scenario_abc]

comparison = compare_multiple_scenarios(
    profile, scenarios, months=3
)

print("SCENARIO SUMMARIES")
for summary in comparison["scenario_summaries"]:
    print(summary)

print("\nMONTH-BY-MONTH COMPARISON")
for month in comparison["monthly_comparison"]:
    print(month)