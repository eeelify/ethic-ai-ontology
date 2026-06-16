import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "ethic-ai-ontology-backend"))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "ethic-ai-ontology-backend", ".env"))

def test():
    try:
        import google.generativeai as genai
        import json
        
        api_key = os.getenv("GEMINI_API_KEY")
        print(f"API KEY present: {bool(api_key)}")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-pro")
        prompt = """
        Analyze the following text about an AI system and extract key ethical, risk, and compliance information.
        Return ONLY a valid JSON object with the following schema, with no markdown formatting:
        {
            "inferred_categories": ["Category 1"],
            "inferred_risks": ["Risk Level 1"],
            "inferred_regulations": ["Regulation 1"],
            "ethical_tensions": [{"name": "Tension Name", "description": "Short explanation"}],
            "ethical_analysis": [{"principle": "Principle", "harm_type": "Harm", "reason": "Reason"}]
        }
        Text: This is a generic text about a totally unknown system.
        """
        print("Calling generate_content...")
        response = model.generate_content(prompt)
        print("Response received.")
        print(response.text)
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test()
