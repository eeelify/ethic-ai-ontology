import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "ethic-ai-ontology-backend"))

from services.reasoning_service import run_inference

if __name__ == "__main__":
    print("Test 1: Biometric system")
    res1 = run_inference(features=["Biometric authentication"], data_types=[])
    print(res1)
    
    print("\nTest 2: General profiling with health data")
    res2 = run_inference(features=["profiling users"], data_types=["Health data"])
    print(res2)

    print("\nTest 3: Normal system")
    res3 = run_inference(features=["text generation"], data_types=["public documents"])
    print(res3)
