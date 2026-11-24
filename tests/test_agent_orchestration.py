
import asyncio
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


# Make the engine folder available for imports.
ENGINE_PATH = Path(__file__).resolve().parents[1] / "src" / "engine"
sys.path.insert(0, str(ENGINE_PATH))

# Use a dummy key because this test will not call OpenAI.
os.environ.setdefault("OPENAI_API_KEY", "test-key-not-used")

import llm_agent as agent


@pytest.mark.parametrize("tool_name", ["add_expense"])
def test_chat_dispatches_tool_and_returns_result(tool_name, monkeypatch):
    # Fake MCP tool information.
    fake_tool = SimpleNamespace(
        name=tool_name,
        description="Add a monthly expense",
        input_schema={},
    )

    # Fake MCP client.
    class FakeMCPClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def list_tools(self):
            return SimpleNamespace(tools=[fake_tool])

        async def call_tool(self, name, arguments):
            self.called_tool = name
            self.called_arguments = arguments

            return SimpleNamespace(
                content=[SimpleNamespace(text="Expense added successfully")],
                is_error=False,
                structuredContent={},
            )

    fake_mcp_client = FakeMCPClient()

    # Replace the real MCP connection with our fake client.
    monkeypatch.setattr(
        agent,
        "Client",
        lambda server: fake_mcp_client,
    )

    # Simulate the LLM requesting an MCP tool.
    fake_function_call = SimpleNamespace(
        type="function_call",
        name=tool_name,
        arguments=json.dumps({
            "name": "gym",
            "amount": 5000,
            "category": "flexible",
        }),
        call_id="call_123",
    )

    first_response = SimpleNamespace(
        output=[fake_function_call],
        id="response_1",
    )

    # Simulate the LLM's final answer after receiving the tool result.
    second_response = SimpleNamespace(
        output=[],
        output_text="Your gym expense was added.",
        id="response_2",
    )

    fake_responses = [first_response, second_response]
    captured_requests = []

    def fake_create_openai_response(
        openai_client,
        request_id,
        **kwargs,
    ):
        captured_requests.append(kwargs)
        return fake_responses.pop(0)

    # Replace the real OpenAI API call with our simulated responses.
    monkeypatch.setattr(
        agent,
        "create_openai_response",
        fake_create_openai_response,
    )

    # Run the actual chat() function.
    answer, response_id = asyncio.run(
        agent.chat("Add a ₹5,000 gym expense")
    )

    # Check that the agent called the correct MCP tool.
    assert fake_mcp_client.called_tool == "add_expense"

    # Check that the arguments were passed correctly.
    assert fake_mcp_client.called_arguments == {
        "name": "gym",
        "amount": 5000,
        "category": "flexible",
    }

    # Check that the MCP result was sent back to the LLM.
    tool_output = captured_requests[1]["input"][0]

    assert tool_output["type"] == "function_call_output"
    assert tool_output["call_id"] == "call_123"
    assert tool_output["output"] == "Expense added successfully"

    # Check the final answer returned by chat().
    assert answer == "Your gym expense was added."
    assert response_id == "response_2"


def test_chat_returns_clarification_without_calling_tool(monkeypatch):
    # Create a fake MCP tool.
    fake_tool = SimpleNamespace(
        name="add_expense",
        description="Add a monthly expense",
        input_schema={},
    )

    class FakeMCPClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def list_tools(self):
            return SimpleNamespace(tools=[fake_tool])

        async def call_tool(self, name, arguments):
            pytest.fail("MCP tool should not be called for clarification")

    fake_mcp_client = FakeMCPClient()

    # Replace the real MCP client with our fake client.
    monkeypatch.setattr(
        agent,
        "Client",
        lambda server: fake_mcp_client,
    )

    # Simulate the LLM asking the user a question.
    fake_response = SimpleNamespace(
        output=[],
        output_text="Which expense category should I use?",
        id="response_clarification",
    )

    def fake_create_openai_response(
        openai_client,
        request_id,
        **kwargs,
    ):
        return fake_response

    # Replace the real OpenAI response function.
    monkeypatch.setattr(
        agent,
        "create_openai_response",
        fake_create_openai_response,
    )

    answer, response_id = asyncio.run(
        agent.chat("Add an expense but don't specify the category")
    )

    # Verify that the clarification is returned.
    assert answer == "Which expense category should I use?"
    assert response_id == "response_clarification"