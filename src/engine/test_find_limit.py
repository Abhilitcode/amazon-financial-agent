
from models import FinancialProfile, FinancialScenario
from find_limit import find_max_affordable_commitment
from simulation import simulate_scenario
from models import FinancialEvent

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

baseline = FinancialScenario(name="Baseline", events=[])

limit = find_max_affordable_commitment(
    profile,
    baseline,
    months=24,
)

print("Maximum affordable monthly commitment:", limit)

# Verify the returned amount
test_event = FinancialEvent(
    name="Limit verification",
    event_type="recurring_expense",
    amount=limit,
    start_month=1,
    duration_months=24,
)

test_scenario = FinancialScenario(
    name="Limit verification",
    events=[test_event],
)

#here we r verifying wheather the limit remains 30k or not. when we get limit as 28k
results = simulate_scenario(profile, test_scenario, months=24)

print("Ending savings at the limit:", results[-1].ending_savings)
print("Buffer safe at the limit:", all(r.buffer_safe for r in results))

# Check whether one extra rupee would be unsafe
extra_event = FinancialEvent(
    name="One rupee above limit",
    event_type="recurring_expense",
    amount=limit + 1,
    start_month=1,
    duration_months=24,
)

extra_scenario = FinancialScenario(
    name="One rupee above limit",
    events=[extra_event],
)

extra_results = simulate_scenario(profile, extra_scenario, months=24)

print("Ending savings with ₹1 extra:", extra_results[-1].ending_savings)
print("Buffer safe with ₹1 extra:", all(r.buffer_safe for r in extra_results))

