
from models import FinancialProfile


def create_test_profile():
    return FinancialProfile(
        monthly_salary=80000,
        other_income=5000,
        current_savings=150000,
        fixed_expenses={"rent": 20000},
        essential_expenses={"groceries": 8000},
        flexible_expenses={"dining": 4000},
    )


# Test 1: Valid expense
profile = create_test_profile()
profile.add_expense("Pet care", 2500, "flexible")
print("Test 1:", profile.flexible_expenses)


# Test 2: Duplicate expense name
profile = create_test_profile()

try:
    profile.add_expense("RENT", 3000, "flexible")
except ValueError as error:
    print("Test 2:", error)


# Test 3: Invalid category
profile = create_test_profile()

try:
    profile.add_expense("Pet care", 2500, "miscellaneous")
except ValueError as error:
    print("Test 3:", error)


# Test 4: Negative amount
profile = create_test_profile()

try:
    profile.add_expense("Pet care", -2500, "flexible")
except ValueError as error:
    print("Test 4:", error)


# Test 5: Empty name
profile = create_test_profile()

try:
    profile.add_expense("   ", 2500, "flexible")
except ValueError as error:
    print("Test 5:", error)
