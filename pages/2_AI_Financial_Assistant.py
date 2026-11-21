
import streamlit as st
import asyncio
import sys
from pathlib import Path

# Make the backend folder available to Python.
ENGINE_PATH = Path(__file__).resolve().parent.parent / "src" / "engine"
sys.path.insert(0, str(ENGINE_PATH))

# Import the existing financial agent and OpenAI client.
from llm_agent import chat, openai_client

# Import our new speech function.
from speech import transcribe_audio


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
# 5. Accept text or voice input
# -------------------------------

prompt = st.chat_input(
    "Type a message or record a voice message...",
    accept_audio=True,
    audio_sample_rate=16000,
    key="financial_chat_input",
    submit_mode="disable",
)

user_message = None

MAX_AUDIO_SIZE = 5 * 1024 * 1024  # 5 MB


if prompt is not None:

    # Do not process text and audio together in this first version.
    if prompt.audio is not None and (prompt.text or "").strip():

        st.warning(
            "Please send either a typed message or a voice recording."
        )

    # Process a voice recording.
    elif prompt.audio is not None:

        if prompt.audio.size > MAX_AUDIO_SIZE:

            st.error(
                "Recording is too large. Please record a shorter message."
            )

        else:

            try:
                with st.spinner("Transcribing your voice..."):

                    user_message = transcribe_audio(
                        prompt.audio,
                        openai_client,
                    )

                if not user_message:
                    st.warning("No speech was detected.")

            except Exception as exc:

                st.error(
                    f"Voice transcription failed: "
                    f"{type(exc).__name__}: {exc}"
                )

    # Process an ordinary typed message.
    else:
        user_message = (prompt.text or "").strip()


# -------------------------------
# 6. Send the message to the agent
# -------------------------------

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

                # Preserve the conversation ID.
                st.session_state.previous_response_id = response_id

                st.markdown(answer)

                # Store the assistant's response.
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": answer,
                })

            except Exception as exc:

                st.error(
                    f"Something went wrong: "
                    f"{type(exc).__name__}: {exc}"
                )
