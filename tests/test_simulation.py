
import sys
from pathlib import Path

import pytest

# Make the engine folder available for the imports used by simulation.py
ENGINE_PATH = Path(__file__).resolve().parents[1] / "src" / "engine"
sys.path.insert(0, str(ENGINE_PATH))

from models import FinancialProfile, FinancialEvent, FinancialScenario
from simulation import (
    is_event_active,
    get_expense_amount,
    calculate_scenario_impact,
    simulate_scenario,
)


def create_test_profile():
    return FinancialProfile(
        monthly_salary=80000,
        other_income=5000,
        current_savings=150000,
        fixed_expenses={"rent": 20000},
        essential_expenses={"groceries": 8000},
        flexible_expenses={"dining": 4000},
        monthly_savings_goal=15000,
        minimum_buffer=30000,
    )


# 1. Event timing tests

def test_event_is_not_active_before_start_month():
    event = FinancialEvent(
        name="Car EMI",
        event_type="recurring_expense",
        amount=10000,
        start_month=3,
    )

    assert is_event_active(event, 2) is False


def test_event_is_active_from_start_month():
    event = FinancialEvent(
        name="Car EMI",
        event_type="recurring_expense",
        amount=10000,
        start_month=3,
    )

    assert is_event_active(event, 3) is True


def test_event_stops_after_duration():
    event = FinancialEvent(
        name="Car EMI",
        event_type="recurring_expense",
        amount=10000,
        start_month=3,
        duration_months=2,
    )

    assert is_event_active(event, 4) is True
    assert is_event_active(event, 5) is False


def test_event_without_duration_remains_active():
    event = FinancialEvent(
        name="Permanent EMI",
        event_type="recurring_expense",
        amount=10000,
        start_month=2,
    )

    assert is_event_active(event, 24) is True


# 2. Expense lookup tests

def test_get_expense_amount_finds_expense():
    profile = create_test_profile()

    assert get_expense_amount(profile, "rent") == 20000


def test_get_expense_amount_rejects_unknown_expense():
    profile = create_test_profile()

    with pytest.raises(ValueError):
        get_expense_amount(profile, "unknown expense")


# 3. Scenario impact tests

def test_recurring_expense_affects_each_active_month():
    profile = create_test_profile()

    event = FinancialEvent(
        name="Car EMI",
        event_type="recurring_expense",
        amount=10000,
        start_month=2,
        duration_months=2,
    )

    scenario = FinancialScenario(
        name="Car purchase",
        events=[event],
    )

    month_1 = calculate_scenario_impact(
        scenario, 1, 85000, profile
    )
    month_2 = calculate_scenario_impact(
        scenario, 2, 85000, profile
    )
    month_4 = calculate_scenario_impact(
        scenario, 4, 85000, profile
    )

    assert month_1 == (0, 0)
    assert month_2 == (10000, 0)
    assert month_4 == (0, 0)


def test_one_time_expense_only_affects_start_month():
    profile = create_test_profile()

    event = FinancialEvent(
        name="Laptop purchase",
        event_type="one_time_expense",
        amount=50000,
        start_month=2,
    )

    scenario = FinancialScenario(
        name="Laptop purchase",
        events=[event],
    )

    assert calculate_scenario_impact(
        scenario, 2, 85000, profile
    ) == (50000, 0)

    assert calculate_scenario_impact(
        scenario, 3, 85000, profile
    ) == (0, 0)


def test_income_change_increases_income():
    profile = create_test_profile()

    event = FinancialEvent(
        name="Salary increase",
        event_type="income_change",
        amount=10000,
        start_month=1,
    )

    scenario = FinancialScenario(
        name="Salary increase",
        events=[event],
    )

    assert calculate_scenario_impact(
        scenario, 1, 85000, profile
    ) == (0, 10000)


def test_percentage_events_calculate_correctly():
    profile = create_test_profile()

    events = [
        FinancialEvent(
            name="Rent increase",
            event_type="expense_percentage_change",
            percentage=25,
            target_expense="rent",
        ),
        FinancialEvent(
            name="Salary increase",
            event_type="income_percentage_change",
            percentage=10,
        ),
    ]

    scenario = FinancialScenario(
        name="Percentage changes",
        events=events,
    )

    scenario_expenses, income_change = calculate_scenario_impact(
        scenario, 1, 85000, profile
    )

    # 25% of rent ₹20,000 = ₹5,000 extra expense
    assert scenario_expenses == 5000

    # 10% of income ₹85,000 = ₹8,500 extra income
    assert income_change == 8500


# 4. Full simulation tests

def test_simulation_without_events():
    profile = create_test_profile()

    scenario = FinancialScenario(name="Base case")

    results = simulate_scenario(profile, scenario, months=3)

    assert len(results) == 3
    assert results[0].ending_savings == 203000
    assert results[1].ending_savings == 256000
    assert results[2].ending_savings == 309000


def test_simulation_applies_recurring_expense_in_correct_months():
    profile = create_test_profile()

    event = FinancialEvent(
        name="Car EMI",
        event_type="recurring_expense",
        amount=10000,
        start_month=2,
        duration_months=2,
    )

    scenario = FinancialScenario(
        name="Car purchase",
        events=[event],
    )

    results = simulate_scenario(profile, scenario, months=4)

    assert results[0].ending_savings == 203000
    assert results[1].ending_savings == 246000
    assert results[2].ending_savings == 289000
    assert results[3].ending_savings == 342000


def test_simulation_applies_one_time_expense_once():
    profile = create_test_profile()

    event = FinancialEvent(
        name="Vacation",
        event_type="one_time_expense",
        amount=50000,
        start_month=2,
    )

    scenario = FinancialScenario(
        name="Vacation",
        events=[event],
    )

    results = simulate_scenario(profile, scenario, months=3)

    assert results[0].ending_savings == 203000
    assert results[1].ending_savings == 206000
    assert results[2].ending_savings == 259000
