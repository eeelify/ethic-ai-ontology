import sys
import os
import json
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), "ethic-ai-ontology-backend"))
load_dotenv(os.path.join(os.path.dirname(__file__), "ethic-ai-ontology-backend", ".env"))

from services.analysis_service import analyze_text
from models.schemas import AnalyzeTextResponse
from pydantic import ValidationError

if __name__ == "__main__":
    try:
        res = analyze_text("Bu sistem kredi başvurularını otomatik olarak değerlendirip insanları profilliyor.")
        # print(json.dumps(res, indent=2))
        try:
            validated = AnalyzeTextResponse(**res)
            print("Validation successful!")
        except ValidationError as ve:
            print("Validation error:", ve.errors())
    except Exception as e:
        import traceback
        traceback.print_exc()
