"""Score recorded agent traces; does not call or charge the live model."""
import argparse, json
from pathlib import Path

def load_jsonl(path):
    rows = {}
    for line_no, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip(): continue
        row = json.loads(line)
        if row["case_id"] in rows: raise ValueError(f"Duplicate case_id at line {line_no}: {row['case_id']}")
        rows[row["case_id"]] = row
    return rows

def evaluate_case(case, trace):
    failures = []
    if trace is None: return {"case_id":case["case_id"],"passed":False,"failures":["Missing trace"]}
    calls = trace.get("tool_calls", [])
    tool = case.get("expected_tool")
    if case.get("must_clarify") and not trace.get("clarification_asked", False): failures.append("Expected clarification.")
    if tool is None and calls: failures.append(f"Expected no tool call before clarification; got {[c.get('name') for c in calls]}.")
    if tool and not any(c.get("name") == tool for c in calls): failures.append(f"Expected tool {tool!r} was not observed.")
    if case.get("must_not_mutate") and trace.get("state_changed") is True: failures.append("Unexpected state mutation.")
    for call in calls:
        if call.get("name") == tool:
            args = call.get("arguments", {})
            for key, expected in case.get("required_argument_values", {}).items():
                if args.get(key) != expected: failures.append(f"Argument {key!r}: expected {expected!r}, got {args.get(key)!r}.")
    return {"case_id":case["case_id"],"passed":not failures,"failures":failures}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--dataset",default="tests/evaluation_cases.json"); p.add_argument("--traces",default="evaluation_traces.jsonl"); a=p.parse_args()
    cases=json.loads(Path(a.dataset).read_text(encoding="utf-8")); traces=load_jsonl(a.traces)
    results=[evaluate_case(c,traces.get(c["case_id"])) for c in cases]; passed=sum(r["passed"] for r in results); total=len(results)
    print(f"Evaluation: {passed}/{total} passed ({passed/total*100 if total else 0:.1f}%)")
    for r in results:
        if not r["passed"]:
            print(f"\nFAIL: {r['case_id']}"); [print("  - "+f) for f in r["failures"]]
    raise SystemExit(0 if passed==total else 1)
if __name__ == "__main__": main()
