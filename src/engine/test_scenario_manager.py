
from models import FinancialEvent, FinancialScenario

scenario = FinancialScenario(name="My Financial Plan")

car = FinancialEvent(
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

scenario.add_event(car)
scenario.add_event(vacation)

print("Scenario:", scenario.name)
print("Number of events:", len(scenario.events))

for event in scenario.events:
    print(event.name, event.event_type, event.amount)

# Test duplicate protection
try:
    duplicate_car = FinancialEvent(
        name="car emi",
        event_type="recurring_expense",
        amount=25000,
    )
    scenario.add_event(duplicate_car)
except ValueError as error:
    print("Duplicate prevented:", error)



# Test updating the car EMI
updated_car = FinancialEvent(
    name="Car EMI",
    event_type="recurring_expense",
    amount=22000,
    start_month=1,
    duration_months=60,
)

scenario.update_event("Car EMI", updated_car)

print("\nAfter updating car EMI:")
for event in scenario.events:
    print(event.name, event.amount)

# Test removing the vacation
removed_event = scenario.remove_event("Vacation")

print("\nRemoved event:", removed_event.name)
print("Remaining events:", len(scenario.events))

for event in scenario.events:
    print(event.name, event.amount)
