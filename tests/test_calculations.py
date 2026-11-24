
from src.engine.models import FinancialProfile
from src.engine.calculations import (
    calculate_total_income,
    calculate_total_fixed_expenses,
    calculate_total_essential_expenses,
    calculate_total_flexible_expenses,
    calculate_total_other_expenses,
    calculate_total_expenses,
    calculate_monthly_free_cash,
    calculate_goal_adjusted_surplus,
)


def create_test_profile():
    return FinancialProfile(
        monthly_salary=80000,
        other_income=5000,
        current_savings=150000,
        fixed_expenses={"Rent": 20000},
        essential_expenses={"Groceries": 15000},
        flexible_expenses={"Shopping": 10000},
        other_expenses={"Miscellaneous": 2000},
        monthly_savings_goal=15000,
        minimum_buffer=30000,
    )


def test_calculate_total_income():
    profile = create_test_profile()

    assert calculate_total_income(profile) == 85000


def test_calculate_total_fixed_expenses():
    profile = create_test_profile()

    assert calculate_total_fixed_expenses(profile) == 20000


def test_calculate_total_essential_expenses():
    profile = create_test_profile()

    assert calculate_total_essential_expenses(profile) == 15000


def test_calculate_total_flexible_expenses():
    profile = create_test_profile()

    assert calculate_total_flexible_expenses(profile) == 10000


def test_calculate_total_other_expenses():
    profile = create_test_profile()

    assert calculate_total_other_expenses(profile) == 2000


def test_calculate_total_expenses():
    profile = create_test_profile()

    assert calculate_total_expenses(profile) == 47000


def test_calculate_monthly_free_cash():
    profile = create_test_profile()

    assert calculate_monthly_free_cash(profile) == 38000


def test_calculate_goal_adjusted_surplus():
    profile = create_test_profile()

    assert calculate_goal_adjusted_surplus(profile) == 23000
