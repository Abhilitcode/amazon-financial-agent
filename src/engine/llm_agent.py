import os
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from mcp import Client
from mcp_server import mcp
import json

# 1. Load the API key from the project's .env file
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY was not found in .env")

# 2. Create the OpenAI client
openai_client = OpenAI(api_key=api_key)


# 3. Discover MCP tools and prepare them for OpenAI
async def get_openai_tools(mcp_client):
    tool_list = await mcp_client.list_tools()

    openai_tools = []

    for tool in tool_list.tools:
        openai_tools.append({
            "type": "function",
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.input_schema,
        })

    return openai_tools



async def main():
    instructions = """
    You are the AI assistant for a financial simulation app.

    Use the available MCP tools to answer financial questions.
    Base all financial conclusions on actual tool results.
    Never invent financial data or simulation results.

    Decide which tool to use based on the user's intent:

    - Use get_profile to inspect the current financial profile.
    - Use simulate for a single independent hypothetical event.
      Do not save hypothetical events to the current scenario.
    - Use add_event when the user explicitly wants an event saved
      to their financial plan.
    - Use update_event or remove_event when the user asks to
      modify or remove an event in the saved plan.
    - Use simulate_current_scenario to analyze all saved events.
    - Use compare to compare alternative scenarios.
    - Use find_limit to calculate the maximum safe commitment.

    Preserve existing saved events when adding new events.
    Do not replace the entire profile unless the user asks to.
    Do not claim an event was saved unless the tool succeeds.
    If essential information is missing, ask the user to clarify.
    Explain results using the actual numbers returned by tools.
    """

    async with Client(mcp) as mcp_client:
        tools = await get_openai_tools(mcp_client)
        #to track prev openai repsonse
        previous_response_id = None

        print(f"Financial Agent ready. {len(tools)} tools available.")
        print("Type 'exit' to stop.\n")

        while True:
            user_message = input("You: ").strip()

            if user_message.lower() in {"exit", "quit"}:
                print("Financial Agent stopped.")
                break

            if not user_message:
                continue

            # Send the user's message to OpenAI
            if previous_response_id is None:
                response = openai_client.responses.create(
                    model="gpt-5-mini",
                    instructions=instructions,
                    input=user_message,
                    tools=tools,
                )
            else:
                response = openai_client.responses.create(
                    model="gpt-5-mini",
                    instructions=instructions,
                    previous_response_id=previous_response_id,
                    input=user_message,
                    tools=tools,
                )


            # Allow up to 5 rounds of tool calls for this message
            for round_number in range(5):
                function_calls = [
                    item for item in response.output
                    if item.type == "function_call"
                ]

                # No pending tool calls: the agent has its final answer.
                if not function_calls:
                    print("\nFinancial Agent:")
                    print(
                        response.output_text
                        or "I couldn't produce a final text response."
                    )
                    break

                tool_outputs = []

                for call in function_calls:
                    print(f"\nCalling MCP tool: {call.name}")

                    try:
                        arguments = json.loads(call.arguments)

                        result = await mcp_client.call_tool(
                            call.name,
                            arguments=arguments,
                        )

                        if result.is_error:
                            output_text = "\n".join(
                                item.text
                                for item in result.content
                                if hasattr(item, "text")
                            ) or "Tool execution failed."

                        else:
                            output_text = "\n".join(
                                item.text
                                for item in result.content
                                if hasattr(item, "text")
                            )

                            if not output_text:
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

                # Send outputs for every call in this response together.
                response = openai_client.responses.create(
                    model="gpt-5-mini",
                    instructions=instructions,
                    previous_response_id=response.id,
                    input=tool_outputs,
                    tools=tools,
                )

            else:
                # Do not reuse an unfinished tool-call response next turn.
                print(
                    "\nThe agent reached its tool-call limit. "
                    "Please send a simpler request."
                )
                previous_response_id = None
                continue

            # Keep the latest completed response for the next user message.
            previous_response_id = response.id



if __name__ == "__main__":
    asyncio.run(main())



