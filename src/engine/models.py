from dataclasses import dataclass, field


@dataclass
class FinancialProfile:
    monthly_salary: float
    other_income: float
    current_savings: float

    fixed_expenses: dict[str, float] = field(default_factory=dict)
    essential_expenses: dict[str, float] = field(default_factory=dict)
    flexible_expenses: dict[str, float] = field(default_factory=dict)

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

        if category not in categories:
            raise ValueError(
                "Category must be fixed, essential, or flexible."
            )

        # 4. Prevent duplicate names across all categories
        existing_names = (
            list(self.fixed_expenses)
            + list(self.essential_expenses)
            + list(self.flexible_expenses)
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


@dataclass
class FinancialScenario:
    name: str
    events: list[FinancialEvent] = field(default_factory=list)

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