from models import FinancialProfile, FinancialScenario, MonthlyResult
from calculations import (
    calculate_total_income,
    calculate_total_expenses,
)


def is_event_active(event, month):
    if month < event.start_month:
        return False

    if event.duration_months is None:
        return True

    end_month = event.start_month + event.duration_months - 1

    return month <= end_month

#profile is financial event for rach expenses. 
def get_expense_amount(profile, target_expense):
    expense_categories = [
        profile.fixed_expenses,
        profile.essential_expenses,
        profile.flexible_expenses,
    ]

    matching_amounts = [
        category[target_expense]
        for category in expense_categories
        if target_expense in category
    ]

    if len(matching_amounts) == 0:
        raise ValueError(
            f"Expense '{target_expense}' was not found in the profile."
        )

    if len(matching_amounts) > 1:
        raise ValueError(
            f"Expense '{target_expense}' exists in multiple categories."
        )

    return matching_amounts[0]

def calculate_scenario_impact(
    scenario,
    month,
    regular_income,
    profile,
):
    scenario_expenses = 0
    income_change = 0

    for event in scenario.events:

        if not is_event_active(event, month):
            continue

        if event.event_type == "recurring_expense":
            scenario_expenses += event.amount

        elif event.event_type == "one_time_expense":
            if month == event.start_month:
                scenario_expenses += event.amount

        elif event.event_type == "income_change":
            income_change += event.amount

        elif event.event_type == "income_percentage_change":
            if event.percentage is None:
                raise ValueError(
                    f"Event '{event.name}' requires a percentage."
                )

            income_change += (
                regular_income * event.percentage / 100
            )

        elif event.event_type == "expense_percentage_change":
            if event.percentage is None:
                raise ValueError(
                    f"Event '{event.name}' requires a percentage."
                )

            if event.target_expense is None:
                raise ValueError(
                    f"Event '{event.name}' requires a target expense."
                )

            original_amount = get_expense_amount(
                profile,
                event.target_expense,
            )

            scenario_expenses += (
                original_amount * event.percentage / 100
            )

    return scenario_expenses, income_change



def simulate_scenario(
    profile: FinancialProfile,
    scenario: FinancialScenario,
    months: int = 24,
):
    results = []

    starting_savings = profile.current_savings

    regular_income = calculate_total_income(profile)
    regular_expenses = calculate_total_expenses(profile)

    for month in range(1, months + 1):

        scenario_expenses, income_change = calculate_scenario_impact(
            scenario,
            month,
            regular_income,
            profile
        )

        income = regular_income + income_change

        monthly_free_cash = (
            income
            - regular_expenses
            - scenario_expenses
        )

        ending_savings = (
            starting_savings
            + monthly_free_cash
        )

        savings_goal_met = (
            monthly_free_cash >= profile.monthly_savings_goal
        )

        buffer_safe = (
            ending_savings >= profile.minimum_buffer
        )

        result = MonthlyResult(
            month=month,
            starting_savings=starting_savings,
            income=income,
            regular_expenses=regular_expenses,
            scenario_expenses=scenario_expenses,
            ending_savings=ending_savings,
            monthly_free_cash=monthly_free_cash,
            savings_goal_met=savings_goal_met,
            buffer_safe=buffer_safe,
        )

        results.append(result)

        starting_savings = ending_savings

    return results