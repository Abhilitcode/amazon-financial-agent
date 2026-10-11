from models import FinancialProfile, FinancialEvent, FinancialScenario, MonthlyResult

from summary import summarize_simulation

from calculations import (
    calculate_total_income,
    calculate_total_fixed_expenses,
    calculate_total_essential_expenses,
    calculate_total_flexible_expenses,
    calculate_total_expenses,
    calculate_monthly_free_cash,
    calculate_goal_adjusted_surplus,
)

from simulation import simulate_scenario

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


scenario = FinancialScenario(
    name="Car + Vacation + Salary Cut",
    events=[car_emi, vacation, salary_cut]
)


print("PROFILE")
print(profile)

print("\nSCENARIO")
print(scenario)

print("\nEVENTS")
for event in scenario.events:
    print(
        event.name,
        "|",
        event.event_type,
        "| ₹", event.amount,
        "| starts:", event.start_month,
        "| duration:", event.duration_months,
    )

print(profile)

print("\nCALCULATIONS")

print("Total income:", calculate_total_income(profile))
print("Fixed expenses:", calculate_total_fixed_expenses(profile))
print("Essential expenses:", calculate_total_essential_expenses(profile))
print("Flexible expenses:", calculate_total_flexible_expenses(profile))
print("Total expenses:", calculate_total_expenses(profile))
print("Monthly free cash:", calculate_monthly_free_cash(profile))
print("Goal-adjusted surplus:", calculate_goal_adjusted_surplus(profile))

print("\nSIMULATION")

results = simulate_scenario(
    profile,
    scenario,
    months=6,
)

for result in results:
    print(
        f"Month {result.month}: "
        f"Starting ₹{result.starting_savings:,.0f} | "
        f"Income ₹{result.income:,.0f} | "
        f"Regular expenses ₹{result.regular_expenses:,.0f} | "
        f"Scenario expenses ₹{result.scenario_expenses:,.0f} | "
        f"Ending ₹{result.ending_savings:,.0f} | "
        f"Goal {'Met' if result.savings_goal_met else 'Not Met'} | "
        f"Buffer {'Safe' if result.buffer_safe else 'Breached'}"
    )

print("\nSUMMARY")

summary = summarize_simulation(
    results,
    profile.minimum_buffer,
)

lowest_savings = summary[0]
buffer_breached = summary[1]
first_buffer_breach_month = summary[2]
savings_goal_missed_months = summary[3]

print(f"Lowest savings: ₹{lowest_savings:,.0f}")
print(f"Buffer breached: {buffer_breached}")
print(f"First buffer breach month: {first_buffer_breach_month}")
print(f"Savings goal missed months: {savings_goal_missed_months}")