
import sys
import asyncio
from pathlib import Path

import streamlit as st

# Make the existing engine files importable
PROJECT_ROOT = Path(__file__).resolve().parent
ENGINE_PATH = PROJECT_ROOT / "src" / "engine"

if str(ENGINE_PATH) not in sys.path:
    sys.path.insert(0, str(ENGINE_PATH))

from llm_agent import chat


# Configure the browser page
st.set_page_config(
    page_title="Agentic Financial Planning & Simulation",
    page_icon="💰",
    layout="centered",
)

# Application heading
st.markdown(
    "<h1 style='font-size: 30px; white-space: nowrap;'>"
    "💰 Agentic Financial Planning &amp; Simulation"
    "</h1>",
    unsafe_allow_html=True,
)

st.caption(
    "Explore financial decisions through conversational "
    "planning and monthly simulations."
)

with st.sidebar:
    st.header("About")
    st.write(
        "Explore your financial profile, test hypothetical "
        "expenses, compare scenarios, and estimate affordable "
        "monthly commitments."
    )
    st.info(
        "Illustrative simulations only. Not professional "
        "financial advice."
    )

# Store the chat history for the current browser session
if "messages" not in st.session_state:
    st.session_state.messages = []

if "previous_response_id" not in st.session_state:
    st.session_state.previous_response_id = None

st.subheader("Financial Assistant")

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept a new message
user_message = st.chat_input(
    "Ask about your finances or test a financial scenario..."
)

if user_message:
    st.session_state.messages.append(
        {"role": "user", "content": user_message}
    )

    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing your financial question..."):
            try:
                answer, response_id = asyncio.run(
                    chat(
                        user_message,
                        st.session_state.previous_response_id,
                    )
                )

                st.markdown(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
                st.session_state.previous_response_id = response_id

            except Exception as exc:
                st.error(
                    f"Something went wrong: "
                    f"{type(exc).__name__}: {exc}"
                )
