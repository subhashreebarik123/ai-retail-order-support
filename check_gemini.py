
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)

print("Starting Gemini test...", flush=True)

try:
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents="Reply with only: Gemini is working"
    )

    print("REQUEST SUCCEEDED", flush=True)
    print("Response:", response.text, flush=True)

except Exception as exc:
    print("REQUEST FAILED", flush=True)
    print("Error type:", type(exc).__name__, flush=True)
    print("Error details:", str(exc), flush=True)
