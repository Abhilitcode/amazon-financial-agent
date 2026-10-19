import asyncio
import sys

sys.path.insert(0, "src/engine")

from mcp import Client, types
from mcp_server import mcp


async def main():
    async with Client(mcp) as client:
        tools = await client.list_tools()
        print("Available tools:", [tool.name for tool in tools.tools])

        # 1. Test get_profile
        profile_result = await client.call_tool(
            "get_profile",
            arguments={},
        )

        print("\nTesting get_profile tool")
        print("Did tool calling fail?:", profile_result.is_error)

        for item in profile_result.content:
            if isinstance(item, types.TextContent):
                print(item.text)

        # 1B. Test set_profile
        print("\nTesting set_profile tool")

        set_profile_result = await client.call_tool(
            "set_profile",
            arguments={
                "monthly_salary": 50000,
                "other_income": 0,
                "current_savings": 100000,
                "fixed_expenses": {"rent": 15000},
                "essential_expenses": {"groceries": 5000},
                "flexible_expenses": {"dining": 2000},
                "monthly_savings_goal": 10000,
                "minimum_buffer": 20000,
            },
        )

        print("Did tool calling fail?:", set_profile_result.is_error)

        for item in set_profile_result.content:
            if isinstance(item, types.TextContent):
                print(item.text)

        
        # 1C. Test add_expense
        print("\nTesting add_expense tool")

        add_expense_result = await client.call_tool(
            "add_expense",
            arguments={
                "name": "medicines",
                "amount": 1500,
                "category": "healthcare",
            },
        )

        print("Did tool calling fail?:", add_expense_result.is_error)

        for item in add_expense_result.content:
            if isinstance(item, types.TextContent):
                print(item.text)


        # 2. Test simulate
        simulation_result = await client.call_tool(
            "simulate",
            arguments={
                "event_name": "Car EMI",
                "event_type": "recurring_expense",
                "amount": 20000,
                "start_month": 1,
                "duration_months": 3,
                "months": 3,
            },
        )

        print("\nTesting simulate tool")
        print("Did tool calling fail?:", simulation_result.is_error)

        for item in simulation_result.content:
            if isinstance(item, types.TextContent):
                print(item.text)

        
        print("\nTesting compare tool")

        compare_result = await client.call_tool(
            "compare",
            arguments={
                "scenarios": [
                    {
                        "name": "Car",
                        "events": [
                            {
                                "name": "Car EMI",
                                "event_type": "recurring_expense",
                                "amount": 20000,
                                "start_month": 1,
                                "duration_months": 3,
                            }
                        ],
                    },
                    {
                        "name": "Car + vacation",
                        "events": [
                            {
                                "name": "Car EMI",
                                "event_type": "recurring_expense",
                                "amount": 20000,
                                "start_month": 1,
                                "duration_months": 3,
                            },
                            {
                                "name": "Vacation",
                                "event_type": "one_time_expense",
                                "amount": 60000,
                                "start_month": 2,
                            },
                        ],
                    },
                ],
                "months": 3,
            },
        )

        print("Did tool calling fail?:", compare_result.is_error)

        for item in compare_result.content:
            if isinstance(item, types.TextContent):
                print(item.text)

        
        # 4. Test find_limit
        print("\nTesting find_limit tool")

        limit_result = await client.call_tool(
            "find_limit",
            arguments={
                "months": 24,
                "events": [],
            },
        )

        print("Did tool calling fail?:", limit_result.is_error)

        for item in limit_result.content:
            if isinstance(item, types.TextContent):
                print(item.text)


if __name__ == "__main__":
    asyncio.run(main())