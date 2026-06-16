import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(os.path.join(os.path.dirname(__file__), "ethic-ai-ontology-backend", ".env"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")
prompt = """
Analyze the following text about an AI system and extract key ethical, risk, and compliance information.
Return ONLY a valid JSON object with the following schema, with no markdown formatting:
{
    "inferred_categories": ["Category 1", ...],
    "inferred_risks": ["Risk Level 1", ...],
    "inferred_regulations": ["Regulation 1", ...],
    "ethical_tensions": [{"name": "Tension Name", "description": "Short explanation"}],
    "ethical_analysis": [{"principle": "Principle", "harm_type": "Harm", "reason": "Reason"}]
}
If no specific risks or categories are found, infer them logically based on the AI use-case described.
Text: This is a generic text about a totally unknown system.
"""
res = model.generate_content(prompt)
print(res.text)
