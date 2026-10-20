from dataclasses import dataclass, field
from math import isfinite

@dataclass
class FinancialProfile:
    monthly_salary: float
    other_income: float
    current_savings: float

    fixed_expenses: dict[str, float] = field(default_factory=dict)
    essential_expenses: dict[str, float] = field(default_factory=dict)
    flexible_expenses: dict[str, float] = field(default_factory=dict)
    other_expenses: dict[str, float] = field(default_factory=dict)

    monthly_savings_goal: float = 0.0
    minimum_buffer: float = 0.0

    def add_expense(
        self,
        name: str,
        amount: float,
        category: str,
    ) -> None:

        # 1. Validate the expense name
        name = name.strip()

        if not name:
            raise ValueError("Expense name cannot be empty.")

        # 2. Validate the amount
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise ValueError("Expense amount must be a number.")

        if amount < 0 or amount == float("inf") or amount == float("-inf") or amount != amount:
            raise ValueError("Expense amount must be finite and non-negative.")

        # 3. Select the correct expense category
        
        categories = {
            "fixed": self.fixed_expenses,
            "essential": self.essential_expenses,
            "flexible": self.flexible_expenses,
        }

        category = category.strip().lower()

        # Unknown categories go into other_expenses
        if category not in categories:
            categories[category] = self.other_expenses


        # 4. Prevent duplicate names across all categories
        existing_names = (
            list(self.fixed_expenses)
            + list(self.essential_expenses)
            + list(self.flexible_expenses)
            + list(self.other_expenses)
        )

        if any(existing.casefold() == name.casefold() for existing in existing_names):
            raise ValueError(
                f"Expense '{name}' already exists in the profile."
            )

        # 5. Add the expense to the selected dictionary
        categories[category][name] = amount


@dataclass
class FinancialEvent:
    name: str
    event_type: str
    amount: float = 0.0
    start_month: int = 1
    duration_months: int | None = None
    percentage: float | None = None
    target_expense: str | None = None

    def __post_init__(self):
        # 1. Validate event name
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Event name cannot be empty.")

        # 2. Validate event type
        valid_event_types = {
            "recurring_expense",
            "one_time_expense",
            "income_change",
            "income_percentage_change",
            "expense_percentage_change",
        }

        if not isinstance(self.event_type, str):
            raise ValueError("Event type must be a string.")

        self.event_type = self.event_type.strip().lower()

        if self.event_type not in valid_event_types:
            raise ValueError(
                f"Unsupported event type: {self.event_type}"
            )

        # 3. Validate start month
        if (
            isinstance(self.start_month, bool)
            or not isinstance(self.start_month, int)
            or self.start_month < 1
        ):
            raise ValueError("Start month must be a positive integer.")

        # 4. Validate duration
        if self.duration_months is not None:
            if (
                isinstance(self.duration_months, bool)
                or not isinstance(self.duration_months, int)
                or self.duration_months < 1
            ):
                raise ValueError(
                    "Duration must be a positive integer or None."
                )

        # 5. Validate amount
        if (
            isinstance(self.amount, bool)
            or not isinstance(self.amount, (int, float))
            or not isfinite(self.amount)
        ):
            raise ValueError("Amount must be a finite number.")

        if (
            self.event_type in {"recurring_expense", "one_time_expense"}
            and self.amount < 0
        ):
            raise ValueError("Expense amount cannot be negative.")

        # 6. Validate percentage for percentage-based events
        percentage_event_types = {
            "income_percentage_change",
            "expense_percentage_change",
        }

        if self.event_type in percentage_event_types:
            if (
                isinstance(self.percentage, bool)
                or not isinstance(self.percentage, (int, float))
                or not isfinite(self.percentage)
            ):
                raise ValueError(
                    f"Event '{self.name}' requires a finite percentage."
                )

        # 7. Expense percentage changes need a target
        if self.event_type == "expense_percentage_change":
            if (
                not isinstance(self.target_expense, str)
                or not self.target_expense.strip()
            ):
                raise ValueError(
                    f"Event '{self.name}' requires a target expense."
                )


@dataclass
class FinancialScenario:
    name: str
    events: list[FinancialEvent] = field(default_factory=list)

    def add_event(self, event: FinancialEvent) -> None:
        # 1. Check that the event has the correct type
        if not isinstance(event, FinancialEvent):
            raise ValueError("Event must be a FinancialEvent object.")

        # 2. Prevent duplicate event names
        for existing_event in self.events:
            if existing_event.name.casefold() == event.name.casefold():
                raise ValueError(
                    f"Event '{event.name}' already exists in this scenario."
                )

        # 3. Add the event to the scenario
        self.events.append(event)

    
    def update_event(
        self,
        event_name: str,
        updated_event: FinancialEvent,
    ) -> None:
        # 1. Validate the updated event
        if not isinstance(updated_event, FinancialEvent):
            raise ValueError("Updated event must be a FinancialEvent object.")

        # 2. Find the event that should be updated
        for index, existing_event in enumerate(self.events):
            if existing_event.name.casefold() == event_name.casefold():

                # 3. Prevent conflicts with another event's name
                for other_index, other_event in enumerate(self.events):
                    if (
                        other_index != index
                        and other_event.name.casefold()
                        == updated_event.name.casefold()
                    ):
                        raise ValueError(
                            f"Event '{updated_event.name}' already exists."
                        )

                # 4. Replace the old event with the updated event
                self.events[index] = updated_event
                
                #return is used inside a function to 
                #send a value back to the caller and immediately exit the function
                return

        # 5. Handle an event name that doesn't exist
        raise ValueError(f"Event '{event_name}' was not found.")

    def remove_event(self, event_name: str) -> FinancialEvent:
        # 1. Find the event to remove
        for index, existing_event in enumerate(self.events):
            if existing_event.name.casefold() == event_name.casefold():

                # 2. Remove and return the event
                return self.events.pop(index)

        # 3. Handle an event name that doesn't exist
        raise ValueError(f"Event '{event_name}' was not found.")



@dataclass
class MonthlyResult:
    month: int
    starting_savings: float
    income: float
    regular_expenses: float
    scenario_expenses: float
    ending_savings: float
    monthly_free_cash: float
    savings_goal_met: bool
    buffer_safe: bool