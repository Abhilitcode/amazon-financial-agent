import json
from pathlib import Path
from evaluation_runner import evaluate_case
DATA=Path(__file__).with_name("evaluation_cases.json")

def test_dataset_ids_and_schema():
    cases=json.loads(DATA.read_text(encoding="utf-8")); ids=[c["case_id"] for c in cases]
    assert len(ids)==len(set(ids)) and len(cases)>=5
    required={"case_id","prompt","expected_tool","must_clarify","must_not_mutate","required_argument_values","purpose"}
    assert all(required <= c.keys() for c in cases)

def test_missing_category_passes_only_with_clarification_and_no_tool():
    case=next(c for c in json.loads(DATA.read_text(encoding="utf-8")) if c["case_id"]=="expense_missing_category")
    good={"tool_calls":[],"clarification_asked":True,"state_changed":False}
    bad={"tool_calls":[{"name":"add_expense","arguments":{"category":"flexible"}}],"clarification_asked":False,"state_changed":True}
    assert evaluate_case(case,good)["passed"]
    assert not evaluate_case(case,bad)["passed"]

def test_expense_case_checks_tool_and_arguments():
    case=next(c for c in json.loads(DATA.read_text(encoding="utf-8")) if c["case_id"]=="add_expense_complete")
    trace={"tool_calls":[{"name":"add_expense","arguments":{"name":"gym","amount":5000,"category":"flexible"}}],"clarification_asked":False,"state_changed":True}
    assert evaluate_case(case,trace)["passed"]
