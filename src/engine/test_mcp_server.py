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

if __name__ == "__main__":
    asyncio.run(main())