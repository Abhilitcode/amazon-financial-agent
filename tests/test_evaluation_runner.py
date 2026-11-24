
import json

import pytest

from evaluation_runner import evaluate_case, load_jsonl


def test_correct_tool_and_arguments_pass():
    case = {
        "case_id": "add_expense_complete",
        "expected_tool": "add_expense",
        "required_argument_values": {
            "name": "gym",
            "amount": 5000,
            "category": "flexible",
        },
    }

    trace = {
        "tool_calls": [
            {
                "name": "add_expense",
                "arguments": {
                    "name": "gym",
                    "amount": 5000,
                    "category": "flexible",
                },
            }
        ],
    }

    result = evaluate_case(case, trace)

    assert result["passed"] is True
    assert result["failures"] == []


def test_wrong_tool_argument_fails():
    case = {
        "case_id": "add_expense_complete",
        "expected_tool": "add_expense",
        "required_argument_values": {
            "amount": 5000,
        },
    }

    trace = {
        "tool_calls": [
            {
                "name": "add_expense",
                "arguments": {
                    "amount": 3000,
                },
            }
        ],
    }

    result = evaluate_case(case, trace)

    assert result["passed"] is False
    assert any(
        "amount" in failure
        for failure in result["failures"]
    )


def test_missing_trace_fails():
    case = {
        "case_id": "add_expense_complete",
        "expected_tool": "add_expense",
    }

    result = evaluate_case(case, None)

    assert result["passed"] is False
    assert "Missing trace" in result["failures"]


def test_duplicate_trace_ids_are_rejected(tmp_path):
    trace_file = tmp_path / "traces.jsonl"

    trace_rows = [
        {"case_id": "case_1"},
        {"case_id": "case_1"},
    ]

    trace_file.write_text(
        "\n".join(json.dumps(row) for row in trace_rows),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate case_id"):
        load_jsonl(trace_file)
