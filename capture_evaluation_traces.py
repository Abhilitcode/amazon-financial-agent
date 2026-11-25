
import asyncio
import json
import sys
from pathlib import Path
from dataclasses import asdict

# Make the engine folder available for imports.
ENGINE_PATH = Path(__file__).resolve().parent / "src" / "engine"
sys.path.insert(0, str(ENGINE_PATH))

import llm_agent as agent
import mcp_server as server


PROJECT_ROOT = Path(__file__).resolve().parent
DATASET_PATH = PROJECT_ROOT / "tests" / "evaluation_cases_30.json"
TRACE_PATH = PROJECT_ROOT / "evaluation_traces.jsonl"


async def capture_evaluations():
    cases = json.loads(
        DATASET_PATH.read_text(encoding="utf-8")
    )

    all_traces = []

    # Keep the original MCP Client class.
    real_client_class = agent.Client

    for case in cases:
        print(f"\nRunning: {case['case_id']}")

        recorded_tool_calls = []

        # Save the current financial state.
        profile_before = asdict(server.profile)
        scenario_before = asdict(server.current_scenario)

        #Its purpose is to act like your original MCP client, but with one extra ability:
        #It records the tool calls made by the agent.
        
        class RecordingClient:
            def __init__(self, mcp_server):
                self.inner = real_client_class(mcp_server)

            async def __aenter__(self):
                self.client = await self.inner.__aenter__()
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return await self.inner.__aexit__(
                    exc_type, exc, tb
                )

            async def list_tools(self):
                return await self.client.list_tools()

            async def call_tool(self, name, arguments):
                recorded_tool_calls.append({
                    "name": name,
                    "arguments": arguments,
                })

                return await self.client.call_tool(
                    name,
                    arguments=arguments,
                )

        # Temporarily use the recording MCP client.
        agent.Client = RecordingClient

        try:
            # Start a fresh conversation for this case.
            answer, response_id = await agent.chat(
                case["prompt"],
                previous_response_id=None,
            )

            # Check whether financial state changed.
            profile_after = asdict(server.profile)
            scenario_after = asdict(server.current_scenario)

            state_changed = (
                profile_before != profile_after
                or scenario_before != scenario_after
            )

            # A clarification should be a question without a tool call.
            clarification_asked = (
                case.get("must_clarify", False)
                and not recorded_tool_calls
                and "?" in answer
            )

            trace = {
                "case_id": case["case_id"],
                "tool_calls": recorded_tool_calls,
                "clarification_asked": clarification_asked,
                "state_changed": state_changed,
            }

            all_traces.append(trace)

            print("Tools called:", [
                call["name"] for call in recorded_tool_calls
            ])
            print("Clarification detected:", clarification_asked)
            print("State changed:", state_changed)
            print("Agent answer:", answer)

        finally:
            # Restore the original MCP Client class.
            agent.Client = real_client_class

            # Restore the original financial profile.
            server.profile = server.FinancialProfile(
                **profile_before
            )

            # Restore the original saved scenario.
            server.current_scenario.name = scenario_before["name"]
            server.current_scenario.events = [
                server.FinancialEvent(**event)
                for event in scenario_before["events"]
            ]

    # Save one JSON object per line.
    TRACE_PATH.write_text(
        "\n".join(
            json.dumps(trace, ensure_ascii=False)
            for trace in all_traces
        ),
        encoding="utf-8",
    )

    print(f"\nSaved {len(all_traces)} traces to:")
    print(TRACE_PATH)


if __name__ == "__main__":
    asyncio.run(capture_evaluations())
