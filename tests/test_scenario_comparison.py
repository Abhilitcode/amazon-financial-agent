
import sys
from pathlib import Path

ENGINE_PATH = Path(__file__).resolve().parents[1] / "src" / "engine"
sys.path.insert(0, str(ENGINE_PATH))

from models import FinancialProfile, FinancialEvent, FinancialScenario
from comparison import compare_scenarios, compare_multiple_scenarios


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


def create_car_scenario():
    event = FinancialEvent(
        name="Car EMI",
        event_type="recurring_expense",
        amount=10000,
        start_month=2,
        duration_months=2,
    )

    return FinancialScenario(
        name="Car purchase",
        events=[event],
    )


def test_compare_two_scenarios():
    profile = create_test_profile()

    base_scenario = FinancialScenario(name="Base case")
    car_scenario = create_car_scenario()

    result = compare_scenarios(
        profile,
        base_scenario,
        car_scenario,
        months=3,
    )

    assert result["scenario_a"]["name"] == "Base case"
    assert result["scenario_b"]["name"] == "Car purchase"

    assert result["scenario_a"]["ending_savings"] == 309000
    assert result["scenario_b"]["ending_savings"] == 289000

    assert result["ending_savings_difference"] == -20000


def test_compare_two_scenarios_monthly_results():
    profile = create_test_profile()

    base_scenario = FinancialScenario(name="Base case")
    car_scenario = create_car_scenario()

    result = compare_scenarios(
        profile,
        base_scenario,
        car_scenario,
        months=3,
    )

    monthly = result["monthly_comparison"]

    assert len(monthly) == 3

    assert monthly[0]["scenario_a_savings"] == 203000
    assert monthly[0]["scenario_b_savings"] == 203000

    assert monthly[1]["scenario_a_savings"] == 256000
    assert monthly[1]["scenario_b_savings"] == 246000

    assert monthly[2]["difference"] == -20000


def test_compare_multiple_scenarios():
    profile = create_test_profile()

    base_scenario = FinancialScenario(name="Base case")
    car_scenario = create_car_scenario()

    result = compare_multiple_scenarios(
        profile,
        [base_scenario, car_scenario],
        months=3,
    )

    summaries = result["scenario_summaries"]

    assert len(summaries) == 2
    assert summaries[0]["name"] == "Base case"
    assert summaries[0]["ending_savings"] == 309000

    assert summaries[1]["name"] == "Car purchase"
    assert summaries[1]["ending_savings"] == 289000


def test_compare_multiple_scenarios_monthly_results():
    profile = create_test_profile()

    base_scenario = FinancialScenario(name="Base case")
    car_scenario = create_car_scenario()

    result = compare_multiple_scenarios(
        profile,
        [base_scenario, car_scenario],
        months=3,
    )

    monthly = result["monthly_comparison"]

    assert len(monthly) == 3

    assert monthly[0]["Base case"] == 203000
    assert monthly[0]["Car purchase"] == 203000

    assert monthly[1]["Base case"] == 256000
    assert monthly[1]["Car purchase"] == 246000
