from neo4j import GraphDatabase


URI = "neo4j+s://ada522e9.databases.neo4j.io"
USER = "ada522e9"
PASSWORD = "PaloXUBb0qARj_ZOPMKNWIE6Jo-RF612wta3ILZu9KM"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


def get_risk_from_graph(text):
    with driver.session() as session:
        result = session.run("""
            MATCH (a:AI_System)-[:HAS_RISK]->(r:Risk)-[:REGULATED_BY]->(k:Regulation)
            WHERE $text CONTAINS a.keyword
            RETURN r.level AS risk_level, collect(k.name) AS regulations
            LIMIT 1
        """, text=text)

        record = result.single()

        if record:
            return {
                "risk_level": record["risk_level"],
                "applicable_regulations": record["regulations"]
            }

        return {
            "risk_level": "Unknown",
            "applicable_regulations": []
        }

def close_driver():
    driver.close()