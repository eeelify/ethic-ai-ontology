import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(os.path.join(os.path.dirname(__file__), "ethic-ai-ontology-backend", ".env"))

api_key = os.getenv("GEMINI_API_KEY")
print(f"API KEY present: {bool(api_key)}")
genai.configure(api_key=api_key)

models_to_try = [
    "gemini-2.5-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro-latest",
    "gemini-pro"
]

prompt = "Hello"

for m_name in models_to_try:
    print(f"Trying {m_name}...")
    try:
        model = genai.GenerativeModel(m_name)
        response = model.generate_content(prompt)
        print(f"Success with {m_name}!")
        break
    except Exception as e:
        print(f"Failed {m_name}: {e}")
