from dotenv import load_dotenv
import os

load_dotenv("../../.env")

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("Success: OpenAI API key loaded.")
else:
    print("Error: API key not found.")