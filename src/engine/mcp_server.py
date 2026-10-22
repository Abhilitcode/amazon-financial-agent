
from dataclasses import asdict

from mcp.server import MCPServer
from models import FinancialProfile
from models import FinancialEvent, FinancialScenario
from simulation import simulate_scenario
from comparison import compare_multiple_scenarios
from find_limit import find_max_affordable_commitment
from typing import Literal

mcp = MCPServer("Amazon Financial Agent")
EventType = Literal[
    "recurring_expense",
    "one_time_expense",
    "income_change",
    "income_percentage_change",
    "expense_percentage_change",
]

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
def set_profile(
    monthly_salary: float,
    other_income: float,
    current_savings: float,
    fixed_expenses: dict[str, float] | None = None,
    essential_expenses: dict[str, float] | None = None,
    flexible_expenses: dict[str, float] | None = None,
    other_expenses: dict[str, float] | None = None,
    monthly_savings_goal: float = 0,
    minimum_buffer: float = 0,
) -> dict:
    """Replace the current financial profile with a user's own profile."""

    global profile

    profile = FinancialProfile(
        monthly_salary=monthly_salary,
        other_income=other_income,
        current_savings=current_savings,
        fixed_expenses=fixed_expenses or {},
        essential_expenses=essential_expenses or {},
        flexible_expenses=flexible_expenses or {},
        other_expenses=other_expenses or {},
        monthly_savings_goal=monthly_savings_goal,
        minimum_buffer=minimum_buffer,
    )

    return asdict(profile)

# Create the scenario once when the server starts
current_scenario = FinancialScenario(
    name="My Financial Plan",
)


@mcp.tool()
def add_expense(name: str, amount: float, category: str) -> dict:
    """Add a monthly expense to the requested expense category."""
    if amount < 0:
        raise ValueError("Expense amount cannot be negative.")

    category_key = category.strip().lower().replace(" ", "_").replace("-", "_")

    category_map = {
        "fixed": "fixed_expenses",
        "fixed_expense": "fixed_expenses",
        "fixed_expenses": "fixed_expenses",
        "essential": "essential_expenses",
        "essential_expense": "essential_expenses",
        "essential_expenses": "essential_expenses",
        "flexible": "flexible_expenses",
        "flexible_expense": "flexible_expenses",
        "flexible_expenses": "flexible_expenses",
        "other": "other_expenses",
        "other_expense": "other_expenses",
        "other_expenses": "other_expenses",
    }

    field_name = category_map.get(category_key)

    if field_name is None:
        raise ValueError(
            "Invalid category. Use fixed_expenses, "
            "essential_expenses, flexible_expenses, or other_expenses."
        )

    expenses = getattr(profile, field_name)
    expenses[name] = amount

    return asdict(profile)

@mcp.tool()
def add_event(
    event_name: str,
    event_type: EventType,
    amount: float = 0,
    start_month: int = 1,
    duration_months: int | None = None,
    percentage: float | None = None,
    target_expense: str | None = None,
) -> dict:
    """Add a financial event to the current scenario."""

    event = FinancialEvent(
        name=event_name,
        event_type=event_type,
        amount=amount,
        start_month=start_month,
        duration_months=duration_months,
        percentage=percentage,
        target_expense=target_expense,
    )

    current_scenario.add_event(event)

    return asdict(current_scenario)


@mcp.tool()
def update_event(
    event_name: str,
    updated_event_name: str,
    event_type: EventType,
    amount: float = 0,
    start_month: int = 1,
    duration_months: int | None = None,
    percentage: float | None = None,
    target_expense: str | None = None,
) -> dict:
    """Update an existing event in the current scenario."""

    updated_event = FinancialEvent(
        name=updated_event_name,
        event_type=event_type,
        amount=amount,
        start_month=start_month,
        duration_months=duration_months,
        percentage=percentage,
        target_expense=target_expense,
    )

    current_scenario.update_event(event_name, updated_event)

    return asdict(current_scenario)


@mcp.tool()
def remove_event(event_name: str) -> dict:
    """Remove an event from the current scenario."""

    removed_event = current_scenario.remove_event(event_name)

    return {
        "message": f"Removed event '{removed_event.name}'.",
        "scenario": asdict(current_scenario),
    }


@mcp.tool()
def simulate_current_scenario(months: int = 24) -> list[dict]:
    """Simulate all events in the current financial plan."""

    results = simulate_scenario(
        profile,
        current_scenario,
        months,
    )

    return [asdict(result) for result in results]


@mcp.tool()
def simulate(
    event_name: str,
    event_type: EventType,
    amount: float = 0,
    start_month: int = 1,
    duration_months: int | None = None,
    percentage: float | None = None,
    target_expense: str | None = None,
    months: int = 24,
) -> list[dict]:
    """Simulate a hypothetical event on top of the saved plan."""

    # Copy existing saved events; do not modify the original plan.
    events = [
        FinancialEvent(**asdict(event))
        for event in current_scenario.events
    ]

    # Add the hypothetical event to the copy.
    hypothetical_event = FinancialEvent(
        name=event_name,
        event_type=event_type,
        amount=amount,
        start_month=start_month,
        duration_months=duration_months,
        percentage=percentage,
        target_expense=target_expense,
    )

    events.append(hypothetical_event)

    scenario = FinancialScenario(
        name="Hypothetical: " + event_name,
        events=events,
    )

    results = simulate_scenario(profile, scenario, months)

    return [asdict(result) for result in results]



@mcp.tool()
def compare(
    scenarios: list[dict],
    months: int = 24,
) -> dict:
    """Compare scenarios, optionally based on the current saved plan."""
    scenario_objects = []

    for scenario_data in scenarios:
        # Copy saved events only; never modify the original plan.
        include_current_plan = scenario_data.get(
            "include_current_plan", True
        )

        events = (
            [
                FinancialEvent(**asdict(event))
                for event in current_scenario.events
            ]
            if include_current_plan
            else []
        )

        # Add hypothetical events to this scenario's copy.
        for event_data in scenario_data.get("events", []):
            event_data = dict(event_data)

            if "event_name" in event_data and "name" not in event_data:
                event_data["name"] = event_data.pop("event_name")
            else:
                event_data.pop("event_name", None)

            events.append(FinancialEvent(**event_data))

        scenario = FinancialScenario(
            name=scenario_data.get("name", "Unnamed Scenario"),
            events=events,
        )

        scenario_objects.append(scenario)

    return compare_multiple_scenarios(
        profile,
        scenario_objects,
        months,
    )


@mcp.tool()
def find_limit(
    months: int = 24,
    events: list[dict] | None = None,
) -> dict:
    """Find the largest additional monthly commitment that maintains
    the minimum savings buffer and meets the monthly savings goal."""

    event_objects = []

    for event_data in (events or []):
        event_data = dict(event_data)

        # Accept either "name" or "event_name" from the AI
        if "event_name" in event_data and "name" not in event_data:
            event_data["name"] = event_data.pop("event_name")
        else:
            event_data.pop("event_name", None)

        event = FinancialEvent(**event_data)
        event_objects.append(event)

    # Copy the saved plan's events without modifying the original.
    saved_events = [
        FinancialEvent(**asdict(event))
        for event in current_scenario.events
    ]

    # Include any additional hypothetical events supplied to the tool.
    base_scenario = FinancialScenario(
        name="Existing financial commitments",
        events=saved_events + event_objects,
    )

    amount = find_max_affordable_commitment(
        profile,
        base_scenario,
        months,
    )

    if amount is None:
        return {
            "status": "unsafe",
            "message": (
                "Your existing financial plan breaches the minimum "
                "savings buffer even without an additional commitment."
            ),
            "maximum_commitment": None,
        }

    return {
        "status": "safe",
        "maximum_commitment": amount,
        "months": months,
    }

