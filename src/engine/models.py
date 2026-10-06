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

@dataclass
class FinancialEvent:
    name: str
    event_type: str
    amount: float
    start_month: int = 1
    duration_months: int | None = None


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