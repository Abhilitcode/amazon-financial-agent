
from dataclasses import asdict

from mcp.server import MCPServer
from models import FinancialProfile
from models import FinancialEvent, FinancialScenario
from simulation import simulate_scenario
from comparison import compare_multiple_scenarios


mcp = MCPServer("Amazon Financial Agent")


profile = FinancialProfile(
    monthly_salary=80000,
    other_income=5000,
    current_savings=150000,
    fixed_expenses={
        "rent": 20000,
        "loan_emi": 15000,
        "insurance": 3000,
    },
    essential_expenses={
        "groceries": 8000,
        "transport": 4000,
        "utilities": 3000,
    },
    flexible_expenses={
        "shopping": 3000,
        "dining": 4000,
        "entertainment": 2000,
    },
    monthly_savings_goal=15000,
    minimum_buffer=30000,
)


@mcp.tool()
def get_profile() -> dict:
    """Return the current financial profile."""
    return asdict(profile)

@mcp.tool()
def simulate(
    event_name: str,
    event_type: str,
    amount: float = 0,
    start_month: int = 1,
    duration_months: int | None = None,
    percentage: float | None = None,
    target_expense: str | None = None,
    months: int = 24,
) -> list[dict]:
    """Simulate a financial event and return monthly results."""

    event = FinancialEvent(
        name=event_name,
        event_type=event_type,
        amount=amount,
        start_month=start_month,
        duration_months=duration_months,
        percentage=percentage,
        target_expense=target_expense,
    )

    scenario = FinancialScenario(
        name=event_name,
        events=[event],
    )

    results = simulate_scenario(profile, scenario, months)

    return [asdict(result) for result in results]


@mcp.tool()
def compare(
    scenarios: list[dict],
    months: int = 24,
) -> dict:
    """Compare multiple financial scenarios and return their results."""
    scenario_objects = []

    for scenario_data in scenarios:
        events = []

        for event_data in scenario_data["events"]:
            event = FinancialEvent(**event_data)
            events.append(event)

        #final scenario object to append
        scenario = FinancialScenario(
            name=scenario_data["name"],
            events=events,
        )

        scenario_objects.append(scenario)

    results = compare_multiple_scenarios(profile, scenario_objects, months)
    
    return results

