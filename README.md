# Agentic Financial Planning & Simulation

An AI-powered financial assistant that helps users explore financial decisions through conversational planning, affordability calculations, and monthly simulations.

## Features

- **Financial Profile:** Retrieve income, expenses, savings, monthly savings goals, and minimum savings buffer.
- **Find My Limit:** Estimate the maximum additional monthly EMI while maintaining the savings goal and minimum buffer.
- **Financial Simulation:** Evaluate hypothetical financial commitments and project their impact on monthly cash flow and savings.
- **Scenario Comparison:** Compare alternative financial decisions over a specified time horizon.
- **MCP Tools:** Connect the conversational AI agent to tools for financial calculations, profile management, and scenario simulation.

## Technology Stack

- Python
- Streamlit
- OpenAI API
- Model Context Protocol (MCP)
- Financial simulation and calculation modules

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

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure your OpenAI API key using a local `.env` file or Streamlit Secrets. Never commit API keys or other secrets to GitHub.

   Example `.env` entry:

   ```text
   OPENAI_API_KEY=your_api_key_here
   ```

5. Start the application:

   ```bash
   streamlit run app.py
   ```

## How It Works

Users interact with a conversational AI agent using natural language. The agent can call MCP tools to retrieve the financial profile, calculate affordability limits, simulate hypothetical commitments, and compare scenarios. The simulation tools calculate projected financial outcomes using the profile and scenario assumptions.

## Important Disclaimer

This application provides illustrative financial simulations for educational and planning purposes only. It does not provide professional financial, investment, lending, or tax advice. Results depend on the accuracy of the profile and assumptions provided.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.