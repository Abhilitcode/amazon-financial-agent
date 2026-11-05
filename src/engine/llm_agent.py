
import os
import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from mcp import Client
from mcp_server import mcp


# Load environment variables from the project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    try:
        import streamlit as st
        api_key = st.secrets["OPENAI_API_KEY"]
    except (ImportError, KeyError, FileNotFoundError):
        pass

if not api_key:
    raise ValueError("OPENAI_API_KEY was not found in environment variables or Streamlit Secrets")

openai_client = OpenAI(api_key=api_key)


INSTRUCTIONS = """
You are the AI assistant for a financial simulation app.

Use the available MCP tools to answer financial questions.
Base all financial conclusions on actual tool results.
Never invent financial data or simulation results.

Choose tools based on user intent:
- Use get_profile to inspect the financial profile.
- Use simulate for a hypothetical financial event.
- Use add_event to save an event to the current plan.
- Use update_event or remove_event to modify saved events.
- Use simulate_current_scenario to analyze the saved plan.
- Use compare to compare financial scenarios.
- Use find_limit to calculate the maximum safe commitment.
- Use add_expense to add a monthly expense to the financial profile.
- Use set_profile only when the user explicitly wants to replace their
  complete financial profile.

IMPORTANT: Clarify the destination before adding an expense when the
user's intention is not clear. There are three different destinations:
1. Financial profile: use add_expense for a regular monthly expense that
   should become part of the user's normal income-and-expense profile.
2. Saved financial plan: use add_event for a one-time, temporary, or
   scheduled financial event that should be saved in the current plan.
3. Hypothetical simulation: use simulate when the user only wants to
   test an expense or event without saving it to the profile or plan.

Do not assume that every expense belongs in the financial profile or
that every recurring expense belongs in the profile. A temporary
recurring expense may be a saved event. If the destination is ambiguous,
ask the user which of the three destinations they want. Explain the
options briefly in ordinary conversational language. Do not call any
state-changing tool until the user has clarified the destination.

Before calling add_expense:
- Confirm that the user wants a regular monthly expense in the financial
  profile.
- If the expense category is missing or unclear, ask which category to
  use: fixed expenses, essential expenses, flexible expenses, or other
  expenses. Do not guess a category.
- Ensure the expense name and amount are known.

Before calling add_event:
- Confirm that the user wants the event saved in the current financial
  plan, rather than added to the profile or tested hypothetically.
- Ask for any essential event details that are missing or ambiguous,
  such as event name, event type, amount, start month, or duration.
- Do not invent a duration or silently convert a temporary expense into
  a permanent profile expense.

Before calling simulate:
- Confirm that the user is asking for a hypothetical, unsaved analysis.
- Ask for any essential simulation details that are missing.

Clarification behavior:
- Ask a natural-language follow-up question; never expose internal
  validation errors, Python exceptions, or raw tool-schema messages.
- If multiple destinations are plausible, present all three choices:
  financial profile, saved financial plan, and hypothetical simulation.
- If only one detail is missing, ask only for that detail.
- Use the user's answer in the next turn. Do not ask again for details
  the user has already provided.
- If the user has not clarified an ambiguous state-changing request,
  do not execute the tool and do not change any financial data.

Preserve existing events when adding new events.
Do not claim a change succeeded unless the tool succeeds.
Explain results using actual tool outputs.
"""


async def get_openai_tools(mcp_client):
    tool_list = await mcp_client.list_tools()  

    return [
        {
            "type": "function",
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.input_schema,
        }
        for tool in tool_list.tools
    ]


async def chat(user_message, previous_response_id=None):
    """Process one user message and return (answer, response_id)."""

    async with Client(mcp) as mcp_client:
        tools = await get_openai_tools(mcp_client)

        if previous_response_id is None:
            response = openai_client.responses.create(
                model="gpt-5-mini",
                instructions=INSTRUCTIONS,
                input=user_message,
                tools=tools,
            )
        else:
            response = openai_client.responses.create(
                model="gpt-5-mini",
                instructions=INSTRUCTIONS,
                previous_response_id=previous_response_id,
                input=user_message,
                tools=tools,
            )

        # Allow up to five rounds of tool calls.
        for _ in range(5):
            function_calls = [
                item for item in response.output
                if item.type == "function_call"
            ]

            if not function_calls:
                return (
                    response.output_text
                    or "I couldn't produce a final text response.",
                    response.id,
                )

            tool_outputs = []

            for call in function_calls:
                try:
                    arguments = json.loads(call.arguments)

                    result = await mcp_client.call_tool(
                        call.name,
                        arguments=arguments,
                    )

                    output_text = "\n".join(
                        item.text
                        for item in (result.content or [])
                        if hasattr(item, "text")
                    )

                    if result.is_error:
                        output_text = (
                            "Tool execution failed: " + output_text
                        )

                    elif not output_text:
                        output_text = str(
                            getattr(result, "structuredContent", {})
                        )

                except Exception as exc:
                    output_text = (
                        f"Tool call failed: {type(exc).__name__}: {exc}"
                    )

                tool_outputs.append({
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": output_text,
                })
            response = openai_client.responses.create(
                model="gpt-5-mini",
                instructions=INSTRUCTIONS,
                previous_response_id=response.id,
                input=tool_outputs,
                tools=tools,
            )

        return (
            "The agent reached its tool-call limit. "
            "Please try a simpler request.",
            None,
        )


async def main():
    previous_response_id = None
    print("Financial Agent ready. Type 'exit' to stop.\n")

    while True:
        user_message = input("You: ").strip()

        if user_message.lower() in {"exit", "quit"}:
            print("Financial Agent stopped.")
            break

        if not user_message:
            continue

        answer, previous_response_id = await chat(
            user_message,
            previous_response_id,
        )

        print(f"\nFinancial Agent:\n{answer}\n")


if __name__ == "__main__":
    asyncio.run(main())
