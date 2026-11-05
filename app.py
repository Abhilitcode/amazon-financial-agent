
import streamlit as st
import pandas as pd
import asyncio
import sys
from pathlib import Path

# Make the backend folder available to Python.
ENGINE_PATH = Path(__file__).parent / "src" / "engine"
sys.path.insert(0, str(ENGINE_PATH))

from mcp import Client
from mcp_server import mcp

st.set_page_config(
    page_title="Agentic Financial Planning & Simulation",
    page_icon="💰",
    layout="wide",
)


async def save_financial_profile(profile_data):
    async with Client(mcp) as mcp_client:

        # Step 1: Save the financial profile.
        save_result = await mcp_client.call_tool(
            "set_profile",
            arguments=profile_data,
        )

        # Stop if saving failed.
        if save_result.is_error:
            return save_result, None

        # Step 2: Retrieve the saved profile.
        profile_result = await mcp_client.call_tool(
            "get_profile"
        )

        return save_result, profile_result


# -------------------------------
# 1. Application heading
# -------------------------------

st.title("💰 Agentic Financial Planning & Simulation")
st.subheader("Financial Setup")

st.caption(
    "Enter your financial details below. "
    "Refer to the sidebar for instructions and supported features."
)

# -------------------------------
# 2. Sidebar instructions
# -------------------------------

with st.sidebar:
    st.header("How to use this application")

    st.write(
        "Complete your financial profile on this page. "
        "The AI Financial Assistant will use these details "
        "to analyse your financial situation."
    )

    st.divider()

    st.subheader("Supported features")

    st.markdown("""
    - View your financial profile
    - Add or modify monthly expenses
    - Test hypothetical expenses
    - Save financial events
    - Compare financial scenarios
    - Find affordable monthly commitments
    """)

    st.info(
        "All simulations are illustrative and "
        "are not professional financial advice."
    )

# -------------------------------
# 3. Sample financial values
# -------------------------------

if "profile_form_initialized" not in st.session_state:

    st.session_state.monthly_salary = 80000
    st.session_state.other_income = 5000
    st.session_state.current_savings = 150000

    st.session_state.fixed_expenses = pd.DataFrame({
        "Expense": ["Rent", "Loan EMI", "Insurance"],
        "Monthly Amount (₹)": [20000, 15000, 3000],
    })

    st.session_state.essential_expenses = pd.DataFrame({
        "Expense": ["Groceries", "Transport", "Utilities"],
        "Monthly Amount (₹)": [8000, 4000, 3000],
    })

    st.session_state.flexible_expenses = pd.DataFrame({
        "Expense": ["Shopping", "Dining", "Entertainment"],
        "Monthly Amount (₹)": [3000, 4000, 2000],
    })

    st.session_state.other_expenses = pd.DataFrame({
        "Expense": [],
        "Monthly Amount (₹)": [],
    })

    st.session_state.monthly_savings_goal = 15000
    st.session_state.minimum_buffer = 30000

    st.session_state.profile_form_initialized = True

# -------------------------------
# 4. Income details
# -------------------------------

st.header("1. Income Details")

col1, col2, col3 = st.columns(3)

with col1:
    st.number_input(
        "Monthly Salary (₹)",
        min_value=0,
        step=1000,
        key="monthly_salary",
    )

with col2:
    st.number_input(
        "Other Monthly Income (₹)",
        min_value=0,
        step=1,
        key="other_income",
    )

with col3:
    st.number_input(
        "Current Savings (₹)",
        min_value=0,
        step=1,
        key="current_savings",
    )

# -------------------------------
# 5. Expense details
# -------------------------------

st.header("2. Monthly Expenses")

st.caption(
    "Edit the expense names and amounts. "
    "You can also add or delete rows."
)

st.subheader("Fixed Expenses")

st.session_state.fixed_expenses = st.data_editor(
    st.session_state.fixed_expenses,
    num_rows="dynamic",
    width="stretch",
    key="fixed_expenses_editor",
)

st.subheader("Essential Expenses")

st.session_state.essential_expenses = st.data_editor(
    st.session_state.essential_expenses,
    num_rows="dynamic",
    width="stretch",
    key="essential_expenses_editor",
)

st.subheader("Flexible Expenses")

st.session_state.flexible_expenses = st.data_editor(
    st.session_state.flexible_expenses,
    num_rows="dynamic",
    width="stretch",
    key="flexible_expenses_editor",
)

st.subheader("Other Expenses")

st.session_state.other_expenses = st.data_editor(
    st.session_state.other_expenses,
    num_rows="dynamic",
    width="stretch",
    key="other_expenses_editor",
)

# -------------------------------
# 6. Savings targets
# -------------------------------

st.header("3. Savings Targets")

col1, col2 = st.columns(2)

with col1:
    st.number_input(
        "Monthly Savings Goal (₹)",
        min_value=0,
        step=1,
        key="monthly_savings_goal",
    )

with col2:
    st.number_input(
        "Minimum Emergency Buffer (₹)",
        min_value=0,
        step=1,
        key="minimum_buffer",
    )

# -------------------------------
# 7. Submit button
# -------------------------------

st.divider()

if st.button("Submit Financial Profile", type="primary", width="stretch"):

    profile_data = {
        "monthly_salary": st.session_state.monthly_salary,
        "other_income": st.session_state.other_income,
        "current_savings": st.session_state.current_savings,

        "fixed_expenses": {},
        "essential_expenses": {},
        "flexible_expenses": {},
        "other_expenses": {},

        "monthly_savings_goal": st.session_state.monthly_savings_goal,
        "minimum_buffer": st.session_state.minimum_buffer,
    }

    # Convert each expense table into a dictionary.
    expense_categories = {
        "fixed_expenses": st.session_state.fixed_expenses,
        "essential_expenses": st.session_state.essential_expenses,
        "flexible_expenses": st.session_state.flexible_expenses,
        "other_expenses": st.session_state.other_expenses,
    }

    for category, dataframe in expense_categories.items():

        cleaned_data = dataframe.dropna()

        profile_data[category] = {
            str(row["Expense"]).strip(): float(row["Monthly Amount (₹)"])
            for _, row in cleaned_data.iterrows()
            if str(row["Expense"]).strip()
        }


    try:
        save_result, profile_result = asyncio.run(
            save_financial_profile(profile_data)
        )

        if save_result.is_error:
            st.error("Could not save your financial profile.")

        elif profile_result is None or profile_result.is_error:
            st.error("Profile saved, but verification failed.")

        else:
            st.success("Financial profile saved successfully!")

            # Navigate to the AI Financial Assistant.
            st.switch_page("pages/2_AI_Financial_Assistant.py")

    except Exception as exc:
        st.error(f"Error saving financial profile: {exc}")
