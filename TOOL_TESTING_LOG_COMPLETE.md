# Financial Agent — MCP Tool Testing Log

**Phase 1 status:** MCP registration and functional tests completed; findings and Phase 2 follow-ups recorded.  
**Purpose:** Keep actual test results and user-experience recommendations before testing tools through the LLM agent.

## Testing approach
1. Test all MCP tools first, then test all tools through the LLM agent.
2. Record observed outputs/errors before changing code.
3. Direct `python -c` commands run in fresh processes unless multiple actions are explicitly performed in one command.
4. Do not repeat passed tests unless a code change requires regression testing.

## Registration — PASS
Command:
```powershell
python -c "from mcp_server import mcp; print([t.name for t in mcp._tool_manager.list_tools()])"
```
All 10 expected tools registered: `get_profile`, `set_profile`, `add_expense`, `add_event`, `update_event`, `remove_event`, `simulate_current_scenario`, `simulate`, `compare`, `find_limit`.

## Tool-by-tool results

### 1. `get_profile` — PASS
Returned expected default profile:
- Salary ₹80,000; other income ₹5,000; savings ₹1,50,000
- Fixed: rent ₹20,000, loan EMI ₹15,000, insurance ₹3,000
- Essential: groceries ₹8,000, transport ₹4,000, utilities ₹3,000
- Flexible: shopping ₹3,000, dining ₹4,000, entertainment ₹2,000
- Other expenses empty; savings goal ₹15,000; minimum buffer ₹30,000
- Derived baseline: income ₹85,000/month, expenses ₹62,000/month, free cash ₹23,000/month.
No issue found.

### 2. `set_profile` — PASS
A separate-process test set salary ₹50,000, other income ₹2,000, savings ₹1,00,000, rent ₹12,000, groceries ₹5,000, shopping ₹1,000, savings goal ₹8,000, buffer ₹20,000. Both `set_profile` and `get_profile` returned matching values. The temporary in-memory profile did not persist to the normal app process. No issue found.

### 3. `add_expense` — PASS for tested valid/invalid cases
- Valid: added `MCP Test Expense` for ₹1,200 under `essential`; `get_profile()` confirmed it.
- Negative amount `-100` raised `ValueError: Expense amount cannot be negative.` Expected.
- Category `entertainment` raised an invalid-category error. Here `entertainment` is an expense name, not a category argument.

**C-002 — Phase 2 UX:** If category or recurrence is unclear, ask the user briefly whether it is recurring monthly and which category to use: Fixed, Essential, Flexible, or Other. Do not expose raw validation errors or silently assign a category.

**`Literal` note:** Not mandatory. It may expose allowed categories more clearly in the MCP schema, but current aliases provide flexibility. Decide after agent testing.

### 4. `add_event` — PASS for valid input; unsupported type rejected
- Valid: added `MCP Test EMI`, type `recurring_expense`, amount ₹1,000, start month 1, duration 3; returned scenario contained the event.
- `event_type='holiday_expense'` raised `ValueError: Unsupported event type: holiday_expense` from `FinancialEvent.__post_init__` in `models.py`.
- Supported types: `recurring_expense`, `one_time_expense`, `income_change`, `income_percentage_change`, `expense_percentage_change`.

**C-003 — Phase 2 UX:** “Holiday expense” is normal user wording, not a mistake. Do not expose the raw error or choose silently. Ask: “Would you like to add this as a one-time expense (for the holiday trip itself) or a recurring expense (a regular monthly cost)?” Wait for the user's choice, and preserve their wording in the event name, e.g. `Holiday expense`. Do not add a new type unless holiday-specific simulation behavior is actually needed.

### 5. `update_event` — PASS for successful update; missing event rejected
- Added `MCP Test EMI` (₹1,000/month, start 1, duration 3), then updated to `MCP Updated EMI` (₹1,500/month, start 2, duration 4). Output contained one updated event, no duplicate.
- Updating `Nonexistent Event` raised `ValueError: Event 'Nonexistent Event' was not found.` It did not silently create an event.

**C-004 — Phase 2 UX:** If wording does not clearly map to a supported event type, ask the user to choose concisely from: Recurring expense, One-time expense, Income change, Income percentage change, Expense percentage change. Wait before calling `add_event` or `update_event`. For “holiday expense,” offer one-time versus recurring when appropriate. Do not list unrelated saved events or over-explain.

### 6. `remove_event` — PASS for successful removal
Added `MCP Remove Test` as a one-time expense, then removed it. Returned `Removed event 'MCP Remove Test'.` and scenario `events: []`. For a missing event, a natural agent response that it could not find the event is sufficient; no special UX flow requested.

### 7. `simulate_current_scenario` — PASS for default 24-month simulation
Returned 24 monthly results. Every month had income ₹85,000, regular expenses ₹62,000, scenario expenses ₹0, monthly free cash ₹23,000, `savings_goal_met=True`, and `buffer_safe=True`. Ending savings after month 24: ₹7,02,000. Check: ₹1,50,000 + (₹23,000 × 24) = ₹7,02,000.

### 8. `simulate` — PASS for hypothetical event and non-mutation
Tested hypothetical recurring expense ₹5,000/month for 3 months:
- Ending savings: month 1 ₹1,68,000; month 2 ₹1,86,000; month 3 ₹2,04,000.
- Free cash fell from ₹23,000 to ₹18,000/month.
- `SAVED PLAN UNCHANGED: True`.
No issue found.

### 9. `compare` — PASS for three scenarios
Compared 3 months, with `include_current_plan=False`:
1. Baseline
2. Car EMI ₹10,000/month for 3 months
3. Car EMI ₹10,000/month plus one-time vacation expense ₹60,000 in month 2

Ending savings: Baseline ₹2,19,000; Car EMI ₹1,89,000; Car EMI + Vacation ₹1,29,000.

| Month | Baseline | Car EMI | Car EMI + Vacation |
|---:|---:|---:|---:|
| 1 | ₹1,73,000 | ₹1,63,000 | ₹1,63,000 |
| 2 | ₹1,96,000 | ₹1,76,000 | ₹1,16,000 |
| 3 | ₹2,19,000 | ₹1,89,000 | ₹1,29,000 |

Vacation cost correctly applied in month 2. No scenario breached the buffer. Car EMI scenarios missed the savings goal in all 3 months. No code change identified; the agent should explain missed savings-goal months as well as ending savings.

### 10. `find_limit` — baseline PASS; unsafe diagnostic needs improvement
- Baseline `find_limit(months=24)` returned `{'status': 'safe', 'maximum_commitment': 8000, 'months': 24}`. This matches ₹23,000 free cash minus ₹15,000 savings goal.
- With hypothetical ₹10,000/month car EMI for 24 months, result was `status='unsafe'`, `maximum_commitment=None`, with message claiming the minimum buffer was breached.
- Inspection of `find_limit.py`: `find_max_affordable_commitment()` returns `None` if `is_commitment_safe(profile, base_scenario, 0, months)` is false. `is_commitment_safe()` requires both `buffer_safe` and `savings_goal_met` for every month. With the EMI, free cash becomes ₹13,000, below the ₹15,000 savings goal. So `unsafe` is consistent with the combined criteria, but the message may be inaccurate because it specifically claims a buffer breach.

**C-005 — recommendation:** Keep the safety calculation unchanged for now. Improve the diagnostic to identify the actual reason: minimum-buffer breach, savings-goal shortfall, or both. Do not claim a buffer breach unless simulation results confirm it. Add regression tests after changing the message. User reported the final baseline check worked; expected baseline limit remains ₹8,000.

## Phase 1 status summary

| Tool | Status | Follow-up |
|---|---|---|
| `get_profile` | PASS | None identified |
| `set_profile` | PASS | None identified |
| `add_expense` | PASS for tested cases | C-002: clarify category/recurrence in agent |
| `add_event` | PASS for valid input; invalid type rejected | C-003: clarify event type |
| `update_event` | PASS for valid update; missing event rejected | C-004: concise event-type clarification |
| `remove_event` | PASS for successful removal | Natural missing-event response is sufficient |
| `simulate_current_scenario` | PASS | None identified |
| `simulate` | PASS | None identified |
| `compare` | PASS for 3 scenarios | Explain savings-goal misses too |
| `find_limit` | Baseline PASS; diagnostic issue identified | C-005: accurate unsafe reason |

## Phase 2 — LLM-agent test plan
For each tool, record the user prompt, tool(s) called, exact arguments, tool result, final answer, clarification behavior, whether state changed as intended, and pass/fail.

Prioritize:
1. Expense with unclear category/recurrence (C-002).
2. “Holiday expense”; confirm one-time vs recurring clarification (C-003).
3. Ambiguous event update; confirm supported-type clarification when needed (C-004).
4. Affordable commitment when savings goal is missed; ensure no false claim of buffer breach (C-005).
5. Scenario comparison; explain ending savings and missed savings-goal months.

## Change log
- **C-001 — compare event preservation:** Previous issue: scenario events could be dropped when creating `FinancialScenario`. Current code passes `events=events`; earlier 12-month test was reported passing, and the current 3-scenario comparison passed.
- **C-002 — expense clarification:** Ask category/recurrence when unclear; don't expose raw validation errors or silently classify.
- **C-003 — add-event clarification:** Ask one-time vs recurring for “holiday expense” when appropriate.
- **C-004 — event-type clarification:** Present supported choices concisely and wait; don't list unrelated saved events or over-explain.
- **C-005 — find-limit diagnostic:** Report the actual unsafe reason (buffer breach, savings-goal shortfall, or both).

