
from dataclasses import asdict

from mcp.server import MCPServer
from models import FinancialProfile


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
