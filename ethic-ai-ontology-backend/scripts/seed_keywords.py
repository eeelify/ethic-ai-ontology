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
        "ethical_tensions": ["Fairness_vs_Accuracy", "HumanOversight_vs_AutomationEfficiency"],
    },
    {
        "keyword": "biometric",
        "ai_category": "BiometricSystem",
        "risk_level": "ProhibitedRisk",
        "regulations": ["EU_AI_Act_Art_5", "KVKK_Art_6", "GDPR_Art_9"],
        "ethical_tensions": ["Privacy_vs_Transparency", "Security_vs_Explainability"],
    },
    {
        "keyword": "surveillance",
        "ai_category": "SurveillanceSystem",
        "risk_level": "ProhibitedRisk",
        "regulations": ["EU_AI_Act_Art_5"],
        "ethical_tensions": ["Safety_vs_Autonomy", "Privacy_vs_Transparency"],
    },
    {
        "keyword": "healthcare",
        "ai_category": "HealthcareAI",
        "risk_level": "HighRisk",
        "regulations": ["GDPR_Art_9", "KVKK_Art_6"],
        "ethical_tensions": ["Safety_vs_Autonomy", "DataMinimization_vs_Performance"],
    },
    {
        "keyword": "personal data",
        "ai_category": "DataProcessingAI",
        "risk_level": "MediumRisk",
        "regulations": ["GDPR_Art_5", "KVKK_Art_4"],
        "ethical_tensions": ["Accountability_vs_Privacy", "DataMinimization_vs_Performance"],
    },
    {
        "keyword": "emotion recognition",
        "ai_category": "EmotionRecognitionAI",
        "risk_level": "ProhibitedRisk",
        "regulations": ["EU_AI_Act_Art_5"],
        "ethical_tensions": ["Privacy_vs_Transparency", "BiasMitigation_vs_ModelFidelity"],
    },
]

TENSIONS_DETAILS = {
    "Privacy_vs_Transparency": {
        "description": "The system requires explainability and transparency while simultaneously processing sensitive personal information.",
        "severity": "High",
        "recommendation": "Use privacy-preserving explainability techniques and controlled disclosure mechanisms.",
        "conflicting_principles": ["Privacy", "Transparency"]
    },
    "Fairness_vs_Accuracy": {
        "description": "Optimizing purely for predictive accuracy may lead to biased outcomes for underrepresented demographic groups.",
        "severity": "Medium",
        "recommendation": "Apply bias mitigation algorithms (e.g. reweighing or adversarial debiasing) even if they slightly reduce accuracy.",
        "conflicting_principles": ["Fairness", "Accuracy"]
    },
    "HumanOversight_vs_AutomationEfficiency": {
        "description": "Requiring human-in-the-loop oversight slows down processing speed and reduces automation scale benefits.",
        "severity": "High",
        "recommendation": "Establish clear thresholds for automated decisions vs decisions requiring mandatory human review.",
        "conflicting_principles": ["HumanOversight", "AutomationEfficiency"]
    },
    "Security_vs_Explainability": {
        "description": "Providing highly detailed explainability of model decisions might reveal proprietary code or make the system vulnerable to adversarial attacks.",
        "severity": "Medium",
        "recommendation": "Provide explanation details at an aggregated or abstracted level to prevent code leakage and model extraction attacks.",
        "conflicting_principles": ["Security", "Explainability"]
    },
    "Safety_vs_Autonomy": {
        "description": "Intervening to ensure the safety of the user or system overrides and restricts the autonomy of the user.",
        "severity": "High",
        "recommendation": "Implement layered intervention protocols that prioritize safety in critical risk scenarios while maximizing user options.",
        "conflicting_principles": ["Safety", "Autonomy"]
    },
    "Accountability_vs_Privacy": {
        "description": "Maintaining detailed log traces for accountability and auditing conflicts with data minimization and privacy objectives.",
        "severity": "Medium",
        "recommendation": "Anonymize/pseudonymize log records and use cryptographic proofs for audit trails.",
        "conflicting_principles": ["Accountability", "Privacy"]
    },
    "DataMinimization_vs_Performance": {
        "description": "Minimizing the volume of personal data collected reduces the training quality and predictive capabilities of the model.",
        "severity": "Low",
        "recommendation": "Leverage synthetic data generation or federated learning techniques to train models without raw data centralization.",
        "conflicting_principles": ["DataMinimization", "Performance"]
    },
    "BiasMitigation_vs_ModelFidelity": {
        "description": "Modifying input features or decision bounds to mitigate bias can alter model fidelity relative to historical training data.",
        "severity": "Medium",
        "recommendation": "Establish key performance indicators (KPIs) that evaluate bias mitigation alongside model fidelity metrics.",
        "conflicting_principles": ["BiasMitigation", "ModelFidelity"]
    }
}

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
    print("Connecting to Neo4j to seed keywords and ethical tensions...")
    with get_session() as session:
        # 1. Seed Tensions and conflicting principles
        for name, details in TENSIONS_DETAILS.items():
            p1, p2 = details["conflicting_principles"]
            session.run(
                """
                MERGE (t:EthicalTension {name: $name})
                SET t.description = $description,
                    t.severity = $severity,
                    t.recommendation = $recommendation
                WITH t
                MERGE (p1:EthicalPrinciple {name: $p1})
                MERGE (p2:EthicalPrinciple {name: $p2})
                MERGE (p1)-[:CONFLICTS_WITH]->(p2)
                MERGE (t)-[:INVOLVES_PRINCIPLE]->(p1)
                MERGE (t)-[:INVOLVES_PRINCIPLE]->(p2)
                """,
                name=name,
                description=details["description"],
                severity=details["severity"],
                recommendation=details["recommendation"],
                p1=p1,
                p2=p2
            )
            print(f"  [OK]  EthicalTension '{name}' seeded (conflicting {p1} <-> {p2})")

        # 2. Seed Keywords, AI_Category, Regulations
        for entry in KEYWORD_DATA:
            session.run(
                CYPHER,
                keyword=entry["keyword"],
                ai_category=entry["ai_category"],
                risk_level=entry["risk_level"],
                regulations=entry["regulations"],
            )
            print(f"  [OK]  Keyword '{entry['keyword']}' -> {entry['ai_category']} [{entry['risk_level']}]")

            # 3. Link AI_Category -> EthicalTension
            for tension_name in entry.get("ethical_tensions", []):
                session.run(
                    """
                    MATCH (cat:AI_Category {name: $cat_name})
                    MATCH (t:EthicalTension {name: $tension_name})
                    MERGE (cat)-[:MAY_CREATE_TENSION]->(t)
                    """,
                    cat_name=entry["ai_category"],
                    tension_name=tension_name
                )
                print(f"    [TENSION LINK] {entry['ai_category']} -[:MAY_CREATE_TENSION]-> {tension_name}")

    print("\nSeed complete.")


if __name__ == "__main__":
    seed()
