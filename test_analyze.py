import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "ethic-ai-ontology-backend"))

from services.analysis_service import analyze_text

def test():
    res = analyze_text("This is a generic text about a totally unknown system.")
    print("Result:")
    print(res)

if __name__ == "__main__":
    test()
