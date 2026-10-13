
from models import FinancialEvent


def check_rejected(label, **kwargs):
    try:
        FinancialEvent(**kwargs)
        print(f"FAIL: {label} was accepted")
    except ValueError as error:
        print(f"PASS: {label} rejected — {error}")


# Test 1: A valid recurring expense
event = FinancialEvent(
    name="Car EMI",
    event_type="recurring_expense",
    amount=20000,
    start_month=1,
    duration_months=60,
)
print("PASS: Valid event created:", event.name)

# Test 2: Invalid start month
check_rejected(
    "Start month zero",
    name="Car EMI",
    event_type="recurring_expense",
    amount=20000,
    start_month=0,
)


# Test 3: Invalid duration
check_rejected(
    "Negative duration",
    name="Car EMI",
    event_type="recurring_expense",
    amount=20000,
    start_month=1,
    duration_months=-2,
)


# Test 4: Unsupported event type
check_rejected(
    "Unknown event type",
    name="Car EMI",
    event_type="car_payment",
    amount=20000,
)


# Test 5: Missing percentage
check_rejected(
    "Missing percentage",
    name="Salary reduction",
    event_type="income_percentage_change",
    start_month=2,
)


# Test 6: Missing expense target
check_rejected(
    "Missing target",
    name="Rent increase",
    event_type="expense_percentage_change",
    percentage=10,
    start_month=2,
)


# Test 7: Negative expense amount
check_rejected(
    "Negative expense",
    name="Car EMI",
    event_type="recurring_expense",
    amount=-20000,
)


# Test 8: Valid percentage reduction
event = FinancialEvent(
    name="Dining reduction",
    event_type="expense_percentage_change",
    percentage=-25,
    target_expense="dining",
    start_month=1,
    duration_months=None,
)
print("PASS: Negative percentage accepted:", event.percentage)
