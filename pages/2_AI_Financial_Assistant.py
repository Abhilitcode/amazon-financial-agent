
import streamlit as st
import asyncio
import sys
from pathlib import Path

# Make the backend folder available to Python.
ENGINE_PATH = Path(__file__).resolve().parent.parent / "src" / "engine"
sys.path.insert(0, str(ENGINE_PATH))

# Import the existing AI agent.
from llm_agent import chat


# -------------------------------
# 1. Page configuration
# -------------------------------

st.title("🤖 AI Financial Assistant")

st.caption(
    "Ask questions about your finances, "
    "simulate financial decisions, and manage your financial plan."
)


# -------------------------------
# 2. Initialize chat memory
# -------------------------------

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "previous_response_id" not in st.session_state:
    st.session_state.previous_response_id = None


# -------------------------------
# 3. Sidebar
# -------------------------------

with st.sidebar:
    st.header("AI Financial Assistant")

    st.write(
        "Your assistant can analyse your financial profile, "
        "run simulations, and manage saved financial events."
    )

    st.divider()
    
    #starts a fresh conversation rather than continuing the old one.
    if st.button("Clear Chat", width="stretch"):
        st.session_state.chat_messages = []
        st.session_state.previous_response_id = None
        st.rerun()


# -------------------------------
# 4. Display previous messages
# -------------------------------

for message in st.session_state.chat_messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -------------------------------
# 5. Accept a new message
# -------------------------------

user_message = st.chat_input("Ask something about your finances...")

if user_message:

    # Display and store the user's message.
    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_message,
    })

    with st.chat_message("user"):
        st.markdown(user_message)

    # Generate the AI response.
    with st.chat_message("assistant"):

        with st.spinner("Analysing your financial information..."):

            try:
                answer, response_id = asyncio.run(
                    chat(
                        user_message,
                        st.session_state.previous_response_id,
                    )
                )

                # Preserve the conversation ID for the next message.
                st.session_state.previous_response_id = response_id

                st.markdown(answer)

                # Store the assistant's response.
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": answer,
                })

            except Exception as exc:
                st.error(f"Something went wrong: {exc}")
