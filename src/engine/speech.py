def transcribe_audio(audio_file, openai_client):
    """
    Convert a recorded voice message into text.
    Currently supports English and Hindi.
    """

    audio_bytes = audio_file.getvalue()

    if not audio_bytes:
        raise ValueError("The recorded audio is empty.")

    transcription = openai_client.audio.transcriptions.create(
        model="gpt-transcribe",
        file=(
            audio_file.name or "voice-message.wav",
            audio_bytes,
            audio_file.type or "audio/wav",
        ),
    )

    # Get the language detected by OpenAI
    detected_languages = [
        language.code for language in (transcription.languages or [])
    ]

    # Check whether the language was identified
    if not detected_languages:
        raise ValueError(
            "We couldn't identify the language. Please try again."
        )

    # Allow only English and Hindi
    supported_languages = {"en", "hi"}

    if not all(
        language in supported_languages
        for language in detected_languages
    ):
        raise ValueError(
            "Currently, voice input supports only English and Hindi. "
            "Please try again in one of these languages."
        )

    transcribed_text = transcription.text.strip()

    if not transcribed_text:
        raise ValueError("No speech was detected. Please try again.")

    return transcribed_text