
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

    return all(result.buffer_safe for result in results)


def find_max_affordable_commitment(profile, base_scenario, months=24):
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
