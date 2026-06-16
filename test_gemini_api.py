import sys
import os
import json
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), "ethic-ai-ontology-backend"))
load_dotenv(os.path.join(os.path.dirname(__file__), "ethic-ai-ontology-backend", ".env"))

from services.analysis_service import analyze_text

if __name__ == "__main__":
    res = analyze_text("Bu sistem kredi başvurularını otomatik olarak değerlendirip insanları profilliyor. Sistem tamamen insan denetimine (human oversight) tabiidir ve rıza alınmıştır.")
    print("Inferred Categories:", res.get("inferred_categories"))
    print("Detected Triggers:", res.get("detected_risk_triggers"))
    print("Detected Safeguards:", res.get("detected_safeguards"))
    print("Initial Risk:", res.get("initial_risk_level"))
    print("Final Risk:", res.get("final_risk_level"))
