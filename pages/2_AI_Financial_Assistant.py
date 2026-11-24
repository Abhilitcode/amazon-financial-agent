
import streamlit as st
import asyncio
import sys
import json
from pathlib import Path

# -------------------------------
# Make the backend folder available
# -------------------------------

ENGINE_PATH = Path(__file__).resolve().parent.parent / "src" / "engine"
sys.path.insert(0, str(ENGINE_PATH))


# -------------------------------
# Import the existing financial agent
# -------------------------------

from llm_agent import chat, openai_client


# -------------------------------
# Import the existing voice input function
# -------------------------------

from speech import transcribe_audio


# -------------------------------
# 1. Browser-based speech output
# -------------------------------

def render_speech_controls(text):

    # Convert the assistant's response into a safe JavaScript string.
    # This prevents special characters from breaking the HTML.
    safe_text = json.dumps(text).replace("<", "\\u003c")

    html_code = r"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 4px;
            }

            .controls {
                display: flex;
                gap: 10px;
                align-items: center;
            }

            button {
                padding: 8px 16px;
                border-radius: 8px;
                border: 1px solid #888;
                cursor: pointer;
                font-size: 14px;
            }

            #playButton {
                background-color: #2563eb;
                color: white;
                border: none;
            }

            #stopButton {
                background-color: #e5e7eb;
                color: black;
            }
        </style>
    </head>

    <body>

        <div class="controls">
            <button id="playButton">Play</button>
            <button id="stopButton">Stop</button>
        </div>

        <script>
            const text = __SPEECH_TEXT__;

            const synth = window.speechSynthesis;

            const playButton = document.getElementById("playButton");
            const stopButton = document.getElementById("stopButton");

            let chunks = [];
            let currentChunk = 0;
            let stopped = false;

            // Cancel speech that may have been playing before this
            // speech control component was loaded.
            synth.cancel();


            // -------------------------------
            // Detect Hindi or English
            // -------------------------------

            function detectLanguage(text) {

                // Hindi text usually contains Devanagari characters.
                const hindiPattern = /[\u0900-\u097F]/;

                if (hindiPattern.test(text)) {
                    return "hi-IN";
                }

                return "en-US";
            }


            // -------------------------------
            // Select a suitable browser voice
            // -------------------------------

            function selectVoice(language) {

                const voices = synth.getVoices();

                // First try to find the exact language.
                let voice = voices.find(
                    voice => voice.lang.toLowerCase() === language.toLowerCase()
                );

                // If the exact voice is unavailable,
                // try another voice for the same language.
                if (!voice) {

                    const languageCode = language.split("-")[0].toLowerCase();

                    voice = voices.find(
                        voice => voice.lang.toLowerCase().startsWith(languageCode)
                    );
                }

                return voice || null;
            }


            // -------------------------------
            // Split long text into small chunks
            // -------------------------------

            function splitText(text) {

                // Keep chunks reasonably short so browser speech
                // handles long responses more reliably.
                const cleanText = text.replace(/\s+/g, " ").trim();

                return cleanText.match(/[\s\S]{1,220}/g) || [];
            }


            // -------------------------------
            // Speak the current chunk
            // -------------------------------

            function speakNextChunk() {

                if (stopped) {
                    return;
                }

                // If every chunk has been spoken, reset the button.
                if (currentChunk >= chunks.length) {

                    playButton.textContent = "Play";
                    return;
                }

                const chunk = chunks[currentChunk];

                const language = detectLanguage(chunk);

                const utterance = new SpeechSynthesisUtterance(chunk);

                utterance.lang = language;
                utterance.rate = 1;
                utterance.pitch = 1;

                const voice = selectVoice(language);

                if (voice) {
                    utterance.voice = voice;
                }

                // When this chunk finishes, speak the next one.
                utterance.onend = function () {

                    if (stopped) {
                        return;
                    }

                    currentChunk += 1;

                    speakNextChunk();
                };

                // If speech fails, stop and reset the controls.
                utterance.onerror = function () {

                    stopped = true;

                    synth.cancel();

                    playButton.textContent = "Play";
                };

                synth.speak(utterance);
            }


            // -------------------------------
            // Play / Pause / Resume button
            // -------------------------------

            playButton.addEventListener("click", function () {

                // If speech is currently paused, resume it.
                if (synth.paused) {

                    synth.resume();

                    playButton.textContent = "Pause";

                    return;
                }

                // If speech is currently playing, pause it.
                if (synth.speaking) {

                    synth.pause();

                    playButton.textContent = "Resume";

                    return;
                }

                // Otherwise, start speaking from the beginning.
                stopped = false;

                currentChunk = 0;

                chunks = splitText(text);

                if (chunks.length === 0) {
                    return;
                }

                playButton.textContent = "Pause";

                speakNextChunk();
            });


            // -------------------------------
            // Stop button
            // -------------------------------

            stopButton.addEventListener("click", function () {

                stopped = true;

                synth.cancel();

                currentChunk = 0;

                playButton.textContent = "Play";
            });


            // -------------------------------
            // Stop speech when this component
            // is unloaded
            // -------------------------------

            window.addEventListener("pagehide", function () {

                synth.cancel();
            });

        </script>

    </body>
    </html>
    """

    # Insert the assistant response into the HTML.
    html_code = html_code.replace(
        "__SPEECH_TEXT__",
        safe_text,
    )

    # Display the Play/Pause and Stop buttons.
    st.iframe(
        html_code,
        height=65,
        width="stretch",
        alt="Speech controls",
    )


# -------------------------------
# 2. Page configuration
# -------------------------------

st.title("🤖 AI Financial Assistant")

st.caption(
    "Ask questions about your finances, "
    "simulate financial decisions, and manage your financial plan."
)


# -------------------------------
# 3. Initialize chat memory
# -------------------------------

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "previous_response_id" not in st.session_state:
    st.session_state.previous_response_id = None


# -------------------------------
# 4. Sidebar
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
# 5. Display previous messages
# -------------------------------

for message in st.session_state.chat_messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# -------------------------------
# 6. Accept text or voice input
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
# 7. Send the message to the agent
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


# -------------------------------
# 8. Speech controls for latest response
# -------------------------------

latest_assistant_message = next(
    (
        message
        for message in reversed(st.session_state.chat_messages)
        if message["role"] == "assistant"
    ),
    None,
)

if latest_assistant_message:

    render_speech_controls(
        latest_assistant_message["content"]
    )
