
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Find .env in the project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

# Read the API key securely
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY was not found in .env")

# Create the OpenAI client
client = OpenAI(api_key=api_key)

# Send a simple test message
response = client.responses.create(
    model="gpt-5-mini",
    input="You are the AI assistant for a financial simulation app. Reply with: Financial Agent connection successful."
)

print(response.output_text)
