import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "ethic-ai-ontology-backend"))

from services.reasoning_service import run_contextual_inference

if __name__ == "__main__":
    print("Test 1: Credit Scoring System")
    res1 = run_contextual_inference(triggers=["Credit Scoring AI", "Profiling AI", "Financial Services AI"], safeguards=[], data_types=[])
    print(res1)
