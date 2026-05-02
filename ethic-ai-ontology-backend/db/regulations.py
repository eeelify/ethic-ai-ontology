from typing import Dict, List

from db.connection import run_query


def get_regulations_for_system(system_name: str) -> List[Dict]:
    return run_query(
        """
        MATCH (s:Individual {name: $system_name})
        OPTIONAL MATCH (s)-[:HAS_RISK_LEVEL]->(risk:Individual)
        OPTIONAL MATCH (s)-[:HAS_LEGAL_BASIS]->(legal:Individual)
        OPTIONAL MATCH (s)-[:HAS_DECISION_TYPE]->(decision:Individual)
        OPTIONAL MATCH (s)-[:REQUIRES]->(obligation:Individual)
        WITH s,
             collect(DISTINCT risk.name) AS risks,
             collect(DISTINCT legal.name) AS legal_bases,
             collect(DISTINCT decision.name) AS decisions,
             collect(DISTINCT obligation.name) AS obligations
        WITH risks, legal_bases, decisions, obligations,
             CASE WHEN any(r IN risks WHERE r CONTAINS 'High' OR r CONTAINS 'Unacceptable')
                  THEN ['EU AI Act Article 9 - Risk Management System',
                        'EU AI Act Article 13 - Transparency',
                        'EU AI Act Article 14 - Human Oversight']
                  ELSE ['EU AI Act Article 52 - Transparency Obligations']
             END AS ai_act_regs,
             CASE WHEN any(l IN legal_bases WHERE l CONTAINS 'NoConsent' OR l CONTAINS 'NoExplicit')
                  THEN ['KVKK Article 6 - Processing of Sensitive Data',
                        'GDPR Article 9 - Special Category Data']
                  ELSE []
             END AS privacy_regs
        UNWIND (ai_act_regs + privacy_regs) AS regulation
        RETURN DISTINCT regulation
        ORDER BY regulation
        """,
        {"system_name": system_name},
    )

