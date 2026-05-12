"""
seed_keywords.py
────────────────
Populates Neo4j with keyword-mapping nodes so that analysis_service.py
can fetch them dynamically instead of using a hardcoded dict.

Graph model created here:
  (:Keyword {word: "..."})
      -[:MAPS_TO {risk_level: "..."}]->
  (:AI_Category {name: "..."})
      -[:HAS_REGULATION]->
  (:Regulation {name: "..."})

Run once (idempotent – uses MERGE):
  python scripts/seed_keywords.py
"""

import sys
import os

# Allow imports from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(override=True)

from db.connection import get_session

# ─────────────────────────────────────────────────────────────────────────────
# Keyword → AI_Category mapping data  (formerly KEYWORD_RULES in analysis_service.py)
# ─────────────────────────────────────────────────────────────────────────────
KEYWORD_DATA = [
    {
        "keyword": "hiring",
        "ai_category": "HiringAI",
        "risk_level": "HighRisk",
        "regulations": ["EU_AI_Act_Art_9", "GDPR_Art_22"],
    },
    {
        "keyword": "biometric",
        "ai_category": "BiometricSystem",
        "risk_level": "ProhibitedRisk",
        "regulations": ["EU_AI_Act_Art_5", "KVKK_Art_6", "GDPR_Art_9"],
    },
    {
        "keyword": "surveillance",
        "ai_category": "SurveillanceSystem",
        "risk_level": "ProhibitedRisk",
        "regulations": ["EU_AI_Act_Art_5"],
    },
    {
        "keyword": "healthcare",
        "ai_category": "HealthcareAI",
        "risk_level": "HighRisk",
        "regulations": ["GDPR_Art_9", "KVKK_Art_6"],
    },
    {
        "keyword": "personal data",
        "ai_category": "DataProcessingAI",
        "risk_level": "MediumRisk",
        "regulations": ["GDPR_Art_5", "KVKK_Art_4"],
    },
    {
        "keyword": "emotion recognition",
        "ai_category": "EmotionRecognitionAI",
        "risk_level": "ProhibitedRisk",
        "regulations": ["EU_AI_Act_Art_5"],
    },
]

CYPHER = """
MERGE (kw:Keyword {word: $keyword})
MERGE (cat:AI_Category {name: $ai_category})
  ON CREATE SET cat.risk_level = $risk_level
  ON MATCH  SET cat.risk_level = $risk_level
MERGE (kw)-[:MAPS_TO]->(cat)
WITH cat
UNWIND $regulations AS reg_name
  MERGE (reg:Regulation {name: reg_name})
  MERGE (cat)-[:HAS_REGULATION]->(reg)
"""


def seed():
    with get_session() as session:
        for entry in KEYWORD_DATA:
            session.run(
                CYPHER,
                keyword=entry["keyword"],
                ai_category=entry["ai_category"],
                risk_level=entry["risk_level"],
                regulations=entry["regulations"],
            )
            print(f"  [OK]  Keyword '{entry['keyword']}' -> {entry['ai_category']} [{entry['risk_level']}]")
    print("\nSeed complete.")


if __name__ == "__main__":
    seed()
