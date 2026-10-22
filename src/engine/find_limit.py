
from models import FinancialEvent, FinancialScenario
from simulation import simulate_scenario


def is_commitment_safe(profile, base_scenario, amount, months):
    commitment = FinancialEvent(
        name="Proposed monthly commitment",
        event_type="recurring_expense",
        amount=amount,
        start_month=1,
        duration_months=months,
    )

    test_scenario = FinancialScenario(
        name="Test commitment",
        events=base_scenario.events + [commitment],
    )

    results = simulate_scenario(profile, test_scenario, months)

    return all(
        result.buffer_safe and result.savings_goal_met
        for result in results
    )


def find_max_affordable_commitment(profile, base_scenario, months=24):
    """
    Find the maximum additional recurring monthly commitment that:
    1. Keeps savings at or above the minimum buffer every month.
    2. Meets the monthly savings goal every month.
    3. Accounts for existing events in the base scenario.

    Returns:
        int: Maximum safe additional monthly commitment.
        None: If the existing plan cannot meet both safety conditions
              even with no additional commitment.
    """


    if isinstance(months, bool) or not isinstance(months, int) or months < 1:
        raise ValueError("Months must be a positive integer.")

    if not is_commitment_safe(profile, base_scenario, 0, months):
        return None

    low = 0
    high = 1

    while is_commitment_safe(profile, base_scenario, high, months):
        low = high
        high = high * 2

    while low + 1 < high:
        middle = (low + high) // 2

        if is_commitment_safe(profile, base_scenario, middle, months):
            low = middle
        else:
            high = middle

    return low
