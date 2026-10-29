# Amazon Financial Agent --- Final Testing & Requirements Handoff

**Last updated:** 29 October 2026\
**Status:** MCP direct-tool testing completed earlier; LLM-agent testing
completed for the planned test set. Ready to review/prioritize fixes
before editing code.

## 1. Project files currently supplied

These are the latest source files shared in this conversation. Use these
as the reference versions unless the user provides newer versions:

-   `calculations(2).py`
-   `comparison(2).py`
-   `find_limit(2).py`
-   `llm_agent(4).py`
-   `mcp_server(2).py`
-   `models(2).py`
-   `simulation(2).py`
-   `summary(2).py`

Do not ask the user to upload these again unnecessarily.

## 2. Testing status

### MCP server direct-tool tests

The user previously completed direct testing of all 10 MCP tools and
committed/pushed the Markdown testing log to GitHub. Reported outcomes:

  -----------------------------------------------------------------------
  Tool                                Result / observation
  ----------------------------------- -----------------------------------
  `get_profile`                       Passed; returns profile

  `set_profile`                       Passed in an isolated process;
                                      values persisted within that
                                      process

  `add_expense`                       Valid category passed; negative
                                      amount rejected; invalid category
                                      raised an error

  `add_event`                         Valid recurring event passed;
                                      unsupported event type raised an
                                      error

  `update_event`                      Valid update passed; missing event
                                      reported not found

  `remove_event`                      Valid removal passed; missing event
                                      raised an error

  `simulate_current_scenario`         Passed; monthly simulation returned

  `simulate`                          Passed; hypothetical event
                                      simulated without modifying saved
                                      events

  `compare`                           Passed; multi-scenario comparison
                                      worked after a prior code fix

  `find_limit`                        Normal mode passed; it requires
                                      both buffer safety and monthly
                                      savings goal
  -----------------------------------------------------------------------

The earlier direct MCP test log was reported as
`TOOL_TESTING_LOG_COMPLETE.md`, committed/pushed to GitHub. This handoff
records the reported outcomes; it does not replace that GitHub artifact.

### LLM agent tests

The planned LLM-agent test sequence is complete. Results below are based
on the user-shared terminal outputs and agent responses. The terminal's
OpenAI HTTP `200 OK` messages do **not** independently show which MCP
tool was called or its raw result, and several results are therefore
behavior-level observations rather than proof of tool invocation.

  -----------------------------------------------------------------------
  Test                    Test purpose            Result
  ----------------------- ----------------------- -----------------------
  1                       Show financial profile  Pass at response level

  2                       Add one-time ₹1,200     Partial pass; event was
                          expense                 added, categorization
                                                  clarification came
                                                  after mutation

  3                       Show plan and saved     Pass at response level;
                          events                  event list not
                                                  independently
                                                  verifiable with
                                                  existing tools

  4                       Add permanent monthly   Pass at response level
                          gym expense             

  5                       Add temporary recurring Pass at response level
                          gym event               

  6                       Update gym event amount Pass at response level;
                                                  no duplicate reported

  7                       Simulate current plan   Pass at response level;
                          for six months          figures were internally
                                                  consistent with that
                                                  test state

  8                       Compare four scenarios  Pass at response level;
                          over 12 months          comparison outputs were
                                                  internally consistent

  9                       Produce month-by-month  Pass at response level;
                          comparison table        table aligned with
                                                  scenario summaries

  10                      Verify profile, events, Unverified at raw-tool
                          and non-mutation after  level; later session
                          comparison              state differed from
                                                  earlier state

  25                      Buffer-only             Unsupported capability
                          `find_limit` request    / fail: agent reported
                                                  ₹38,100/month, but code
                                                  only supports enforcing
                                                  buffer and savings goal
                                                  together

  26                      Verify saved state      Partial/unverified:
                          after buffer-only       agent reported four
                          request                 original one-time
                                                  events and no
                                                  hypothetical commitment
                                                  saved, but raw
                                                  saved-event retrieval
                                                  tool is absent

  27                      Negative recurring      Passed at response
                          expense input           level; agent rejected
                                                  negative amount

  28                      Ambiguous "add ₹5,000   Passed at response
                          expense" request        level; agent asked
                                                  whether
                                                  recurring/one-time,
                                                  category, name, and
                                                  start month

  29                      Multi-turn add/update   Passed at response
                          event                   level: agent asked for
                                                  category, added
                                                  `Test Subscription` at
                                                  ₹500/month for months
                                                  1--3, then reported
                                                  updating it to
                                                  ₹700/month without
                                                  changing other fields.
                                                  Raw tool results were
                                                  not logged.

  30                      Remove nonexistent      Passed at response
                          event                   level: agent reported
                                                  removal failed and no
                                                  changes were made. MCP
                                                  server emitted an
                                                  `UnexpectedToolError`
                                                  traceback for
                                                  `remove_event`.

  31                      Duplicate event         Passed at response
                          insertion               level: first
                                                  `Final Test` event at
                                                  ₹1,000/month was
                                                  reported saved;
                                                  duplicate add was
                                                  rejected. MCP server
                                                  emitted a traceback for
                                                  duplicate-name
                                                  `ValueError`. Agent
                                                  reported only one event
                                                  existed, but no
                                                  read-only raw event
                                                  list was available at
                                                  that time.

  Additional              "Show profile with all  Agent listed six
  user-directed check     saved events we         events: four one-time
                          created"                events,
                                                  `Test Subscription` at
                                                  ₹700/month for three
                                                  months, and
                                                  `Final Test` at
                                                  ₹1,000/month ongoing.
                                                  This is an
                                                  LLM-generated summary,
                                                  not independently
                                                  verified raw tool
                                                  output.

  Additional              "Add all six events     Agent claimed it
  user-directed change    under other expenses"   changed each event's
                                                  `target_expense` to
                                                  `other`, not the
                                                  profile's
                                                  `other_expenses`
                                                  dictionary. A
                                                  subsequent profile
                                                  display still showed
                                                  `other_expenses` empty.
                                                  This exposed an
                                                  intent-routing /
                                                  data-model
                                                  misunderstanding.
  -----------------------------------------------------------------------

Note: Test numbering in the conversational flow skipped from 10 to 25
when the later phase resumed; this table preserves the labels used in
the conversation rather than inventing missing tests 11--24.

## 3. Confirmed architecture facts from supplied source code

-   `llm_agent.py` uses OpenAI Responses API with `gpt-5-mini`, loads
    MCP tools, dispatches function calls, and sends tool outputs back to
    the model.
-   The current agent loop does not log MCP tool names, arguments, or
    raw tool results to the terminal. OpenAI HTTP `200 OK` logs alone do
    not prove which tool was called.
-   `mcp_server.py` has ten tools: `get_profile`, `set_profile`,
    `add_expense`, `add_event`, `update_event`, `remove_event`,
    `simulate_current_scenario`, `simulate`, `compare`, and
    `find_limit`.
-   `profile` and `current_scenario` are Python in-memory objects. The
    scenario is initialized empty at server startup. State can reset
    when the process restarts.
-   `get_profile()` returns the profile only; there is no read-only tool
    to return the saved event list/current scenario directly.
-   `add_expense()` changes the relevant dictionary inside `profile`.
-   `set_profile()` replaces the profile.
-   `add_event()`, `update_event()`, and `remove_event()` operate on
    `current_scenario.events`, not on profile expense dictionaries.
-   `simulate_current_scenario()` passes both `profile` and
    `current_scenario` to the simulation engine, so saved events affect
    simulations without being converted into profile expenses.
-   `simulate()` copies saved events, adds a hypothetical event to the
    copy, and simulates without intentionally mutating the saved plan.
-   `compare()` builds scenario copies, optionally including saved
    events, and should not mutate the saved plan.
-   `find_limit.py` currently requires every simulated month to satisfy
    both `result.buffer_safe` and `result.savings_goal_met`. Buffer-only
    mode is not implemented.
-   The `find_limit` wrapper's "unsafe" message can be misleading: the
    search may return `None` because the savings goal is missed, not
    because the buffer is breached.
-   `FinancialScenario.add_event()` rejects duplicate event names
    case-insensitively. This is correct validation behavior, but
    currently exceptions can surface as noisy server tracebacks.

## 4. Requirements and fixes to review

These are requirements/findings, not yet implemented fixes.

### Priority 1 --- Readability and correctness of plan state

1.  Add a read-only `get_saved_events` or `get_current_scenario` MCP
    tool returning the exact saved event records.
2.  Make "show my financial plan" display both the financial profile and
    saved events together.
3.  Add MCP tool-call logging (tool name, arguments, success/error, and
    raw result or safe summary) so debugging can distinguish tool
    results from LLM narration.
4.  Handle tool errors cleanly: invalid input, missing event, and
    duplicate event should return understandable structured errors
    instead of noisy tracebacks wherever supported.

### Priority 2 --- Financial profile vs. saved-event behavior

5.  Make agent instructions and tool descriptions clearly distinguish:
    -   Regular monthly budget expenses stored in `profile` expense
        dictionaries.
    -   Time-bound or one-time events stored in
        `current_scenario.events`.
    -   Hypothetical events used only in `simulate`/`compare`.
6.  If the user asks to add a regular expense to the profile, use
    `add_expense`; if the user asks to add a one-time or scheduled
    event, use `add_event`. Ask clarification if unclear.
7.  Do not blindly add all six test events to `profile.other_expenses`:
    one-time events and recurring events already represented in the
    saved scenario can be double-counted if copied into monthly profile
    budgets. If the product needs category labels for events, keep event
    categorization distinct from regular monthly profile amounts.
8.  Add clear UI/help-manual wording explaining profile vs. saved events
    and how events affect simulations.

### Priority 3 --- Persistence and user experience

9.  Replace or supplement in-memory state with persistent storage so
    profile and events survive MCP server restarts. Select storage
    design during implementation planning; do not assume a database
    choice without review.
10. Build the first-page financial setup UI with profile inputs and a
    side help panel/user manual.
11. Proposed UI flow:
    -   Financial Setup: income, savings, goals, buffer, and regular
        expenses.
    -   Financial Dashboard: summary of income, expense budgets,
        savings, and saved events.
    -   AI Financial Assistant: chat, simulations, comparisons, and
        commitment analysis.
12. Validate financial inputs in the UI and show clear save
    status/errors.

### Priority 4 --- Find-limit correctness and scope

13. Correct the `find_limit` failure message so it reports the actual
    reason the tool cannot find a commitment, distinguishing
    savings-goal failure from buffer breach.
14. Decide explicitly whether buffer-only mode is a product requirement.
    If needed, add a clearly named option/constraint mode and test it.
    Do not claim buffer-only support until implemented.
15. Keep the existing normal `find_limit` behavior (buffer and
    savings-goal constraints together) unless the user explicitly
    approves a behavior change.

### Priority 5 --- Agent reliability and robustness

16. Improve intent routing for regular profile expenses vs saved events
    vs hypothetical scenarios.
17. Keep clarification before mutation when required details are
    missing, as demonstrated by the ambiguous expense test.
18. Add tests for structured tool failures, duplicate names, missing
    names, invalid types/amounts, and ensure the model never claims an
    action succeeded unless tool output confirms it.
19. Avoid repeated tool calls and add sensible loop/error safeguards if
    needed.

## 5. UI help-panel wording (draft requirement)

The setup page should explain in concise language:

-   **Financial Profile:** Your income, current savings, savings goal,
    minimum buffer, and regular monthly expense budgets.
-   **Saved Events:** One-time expenses and scheduled financial changes
    stored separately from the profile.
-   **Simulation:** Applies the saved events to the profile for the
    requested months. One-time events affect their specified month;
    recurring events affect their active duration.
-   **Hypothetical Scenarios:** `simulate` and `compare` can evaluate
    proposed changes without saving them to the plan.
-   **Find My Limit:** Uses the constraints currently supported by the
    tool; in the current implementation both buffer safety and monthly
    savings goal must be satisfied.
-   **Persistence notice:** Until persistent storage is implemented, the
    current in-memory profile and events may reset when the server
    process restarts.

## 6. Current state and next action

-   The direct MCP server testing log was previously reported as
    committed/pushed to GitHub.
-   The LLM-agent behavior tests are complete for the planned test set;
    no further broad testing is needed before a defect review.
-   The next step is to review and prioritize these requirements, then
    make changes deliberately. Do not edit source code until the user
    agrees on the fix order.
-   Treat agent responses as behavior-level evidence only unless raw MCP
    outputs are captured.
-   Do not ask the user to re-upload the eight source files listed above
    unnecessarily.

## 7. User workflow preferences

-   Be concise and direct; use short prompts and one test at a time when
    testing is necessary.
-   Avoid wasting tokens on repetitive tests or re-testing known
    behavior.
-   Keep this Markdown file updated as the ongoing project handoff.
-   Clearly state whether a claim comes from source code, terminal
    output, or the LLM agent's own summary.
