import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(override=True)
from db.connection import get_session

_METRICS_CYPHER = """
MERGE (m1:RiskMetric {name: "LikelihoodScore"})
MERGE (m2:RiskMetric {name: "ImpactScore"})
MERGE (m3:RiskMetric {name: "DetectabilityScore"})
MERGE (m4:RiskMetric {name: "EthicalImpactScore"})
MERGE (m5:RiskMetric {name: "LegalComplianceScore"})
MERGE (m6:RiskMetric {name: "TechnicalRobustnessScore"})
MERGE (m7:RiskMetric {name: "HumanOversightScore"})
MERGE (m8:RiskMetric {name: "DataSensitivityScore"})
MERGE (m9:RiskMetric {name: "CompositeRiskScore"})
SET m9.formula = "(0.25 * EthicalImpactScore) + (0.25 * LegalComplianceScore) + (0.20 * DataSensitivityScore) + (0.15 * TechnicalRobustnessScore) + (0.15 * HumanOversightScore)",
    m9.description = "Composite risk score is calculated in the FastAPI backend using weighted ethical, legal, technical, data sensitivity, and human oversight scores."
"""

_THRESHOLDS_CYPHER = """
MERGE (t1:RiskThreshold {name: "MinimalRiskThreshold"}) SET t1.min = 0, t1.max = 25
MERGE (r1:RiskLevel {name: "MinimalRisk"})
MERGE (t1)-[:THRESHOLD_FOR]->(r1)

MERGE (t2:RiskThreshold {name: "LimitedRiskThreshold"}) SET t2.min = 26, t2.max = 50
MERGE (r2:RiskLevel {name: "LimitedRisk"})
MERGE (t2)-[:THRESHOLD_FOR]->(r2)

MERGE (t3:RiskThreshold {name: "HighRiskThreshold"}) SET t3.min = 51, t3.max = 75
MERGE (r3:RiskLevel {name: "HighRisk"})
MERGE (t3)-[:THRESHOLD_FOR]->(r3)

MERGE (t4:RiskThreshold {name: "UnacceptableRiskThreshold"}) SET t4.min = 76, t4.max = 100
MERGE (r4:RiskLevel {name: "UnacceptableRisk"})
MERGE (t4)-[:THRESHOLD_FOR]->(r4)
"""

def seed_metrics():
    print("Connecting to Neo4j to seed metrics and thresholds...")
    with get_session() as session:
        session.run(_METRICS_CYPHER)
        print("✅ RiskMetric nodes successfully created.")
        
        session.run(_THRESHOLDS_CYPHER)
        print("✅ RiskThreshold nodes and relationships successfully created.")
        
    print("\nDone. Neo4j is now up to date with the new ontology structures.")

if __name__ == "__main__":
    seed_metrics()
