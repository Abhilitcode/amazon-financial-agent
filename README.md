# Agentic Financial Planning & Simulation

An AI-powered financial planning agent that helps users understand what they can afford, simulate hypothetical financial decisions, and compare their long-term impact on cash flow and savings. Built with Python, Streamlit, the OpenAI API, and the Model Context Protocol (MCP), the application combines conversational AI with structured financial tools and deterministic simulation logic.

## Features

### 1. Conversational Financial Assistant
- Interact with the financial assistant using natural-language requests.
- Let the agent select and invoke appropriate financial tools based on the user's request.
- Translate financial questions into structured calculations and scenario simulations.

### 2. Financial Profile Management
- **`get_profile`** — Retrieve the financial profile, including income, expenses, savings, savings goals, and minimum buffer.
- **`set_profile`** — Update the financial profile through the agent's tool interface.

### 3. Expense Management
- **`add_expense`** — Add an expense to the financial profile.
- Organize expenses into the categories supported by the application's financial model.

### 4. Financial Event Management
- **`add_event`** — Add a planned financial event, such as a new EMI or a one-time purchase.
- **`update_event`** — Modify an existing financial event.
- **`remove_event`** — Remove a planned event from the scenario.

### 5. Financial Simulation
- **`simulate_current_scenario`** — Simulate the current financial scenario and examine its projected outcomes.
- **`simulate`** — Evaluate a hypothetical financial decision and estimate its impact on monthly cash flow and savings over time.

### 6. Scenario Comparison
- **`compare`** — Compare alternative financial scenarios over a selected time horizon to understand how different decisions affect projected savings and financial goals.

### 7. Affordability Analysis
- **`find_limit`** — Estimate an affordable additional monthly EMI while considering the configured savings goal and minimum savings buffer.

### 8. MCP-Powered Tool Integration
The application exposes **10 financial-planning tools** through the MCP Python SDK, allowing the conversational agent to interact with structured financial operations rather than relying solely on free-form language-model responses.

### 9. Scenario-Based Financial Planning
- Explore the effects of recurring financial commitments and one-time expenses.
- Examine how changes in income or expenses can affect projected savings.
- Compare financial alternatives before making a commitment.
- Identify potential shortfalls against monthly savings goals.

### 10. Interactive Web Application
- Use a Streamlit-based conversational interface.
- View financial calculations and simulation results without needing to run Python scripts manually.
- Access the deployed application through the project's live demo link.

## Technology Stack

- **Python** — Financial calculations, simulation logic, and application backend.
- **Streamlit** — Interactive web interface.
- **OpenAI API (GPT-5-mini)** — Natural-language interaction and agent-driven tool use.
- **Model Context Protocol (MCP) Python SDK** — Structured integration between the agent and its financial tools.
- **GitHub** — Source control and public repository hosting.
- **Streamlit Community Cloud** — Application deployment.

## The 10 MCP Tools

| Tool | Purpose |
|---|---|
| `get_profile` | Retrieve the current financial profile |
| `set_profile` | Update the financial profile |
| `add_expense` | Add a financial expense |
| `add_event` | Create a planned financial event |
| `update_event` | Update an existing event |
| `remove_event` | Remove an existing event |
| `simulate_current_scenario` | Simulate the current scenario |
| `simulate` | Simulate a hypothetical scenario |
| `compare` | Compare alternative scenarios |
| `find_limit` | Calculate an affordability limit |

## Project Structure

```text
amazon-financial-agent/
├── app.py
├── requirements.txt
├── LICENSE
└── src/
    └── engine/
        ├── llm_agent.py
        ├── mcp_server.py
        ├── models.py
        ├── calculations.py
        ├── simulation.py
        ├── comparison.py
        ├── find_limit.py
        └── summary.py
```

## Setup and Run Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/Abhilitcode/amazon-financial-agent.git
   cd amazon-financial-agent
   ```

2. Create and activate a Python environment.

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure your OpenAI API key using a local `.env` file or Streamlit Secrets. Never commit API keys to GitHub.

5. Start the application:

   ```bash
   streamlit run app.py
   ```

## How It Works

1. The user submits a financial question or request in natural language.
2. The OpenAI-powered agent interprets the request and selects an appropriate tool.
3. The MCP integration provides access to the application's financial operations.
4. Python-based calculation and simulation modules process the profile and scenario assumptions.
5. The agent presents the resulting affordability analysis, projected financial outcomes, or scenario comparison.

## Example Use Cases

- Find an affordable additional monthly EMI while maintaining a savings goal.
- Simulate the impact of taking on a car loan.
- Compare a lower EMI with a higher EMI over 12 months.
- Explore how salary reductions or rent increases could affect savings.
- Add, update, or remove planned financial events and examine their impact.

## Important Disclaimer

This application provides illustrative financial simulations for educational and planning purposes only. It does not provide professional financial, investment, lending, or tax advice. Results depend on the financial profile, configured assumptions, and simulation logic.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
