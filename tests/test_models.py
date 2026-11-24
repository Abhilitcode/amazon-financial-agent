
import pytest

from src.engine.models import FinancialProfile, FinancialEvent


def create_test_profile():
    return FinancialProfile(
        monthly_salary=80000,
        other_income=5000,
        current_savings=150000,
        fixed_expenses={"rent": 20000},
        essential_expenses={"groceries": 8000},
        flexible_expenses={"dining": 4000},
    )


# Expense validation tests

def test_add_valid_expense():
    profile = create_test_profile()

    profile.add_expense("Pet care", 2500, "flexible")

    assert profile.flexible_expenses["Pet care"] == 2500


def test_add_expense_with_unknown_category_goes_to_other():
    profile = create_test_profile()

    profile.add_expense("Pet care", 2500, "miscellaneous")

    assert profile.other_expenses["Pet care"] == 2500


def test_duplicate_expense_name_is_rejected_case_insensitively():
    profile = create_test_profile()

    with pytest.raises(ValueError):
        profile.add_expense("RENT", 3000, "flexible")


def test_negative_expense_is_rejected():
    profile = create_test_profile()

    with pytest.raises(ValueError):
        profile.add_expense("Pet care", -2500, "flexible")


def test_empty_expense_name_is_rejected():
    profile = create_test_profile()

    with pytest.raises(ValueError):
        profile.add_expense("   ", 2500, "flexible")


def test_boolean_expense_amount_is_rejected():
    profile = create_test_profile()

    with pytest.raises(ValueError):
        profile.add_expense("Pet care", True, "flexible")


# Financial event validation tests

def test_valid_recurring_expense_event():
    event = FinancialEvent(
        name="Car EMI",
        event_type="recurring_expense",
        amount=20000,
        start_month=1,
        duration_months=60,
    )

    assert event.name == "Car EMI"
    assert event.amount == 20000


@pytest.mark.parametrize(
    "event_data",
    [
        {
            "name": "Car EMI",
            "event_type": "recurring_expense",
            "amount": 20000,
            "start_month": 0,
        },
        {
            "name": "Car EMI",
            "event_type": "recurring_expense",
            "amount": 20000,
            "duration_months": -2,
        },
        {
            "name": "Car EMI",
            "event_type": "car_payment",
            "amount": 20000,
        },
        {
            "name": "Salary reduction",
            "event_type": "income_percentage_change",
        },
        {
            "name": "Rent increase",
            "event_type": "expense_percentage_change",
            "percentage": 10,
        },
        {
            "name": "Car EMI",
            "event_type": "recurring_expense",
            "amount": -20000,
        },
    ],
)

def test_invalid_financial_events_are_rejected(event_data):
    with pytest.raises(ValueError):
        FinancialEvent(**event_data)


def test_negative_percentage_reduction_is_valid():
    event = FinancialEvent(
        name="Dining reduction",
        event_type="expense_percentage_change",
        percentage=-25,
        target_expense="dining",
        start_month=1,
    )

    assert event.percentage == -25
