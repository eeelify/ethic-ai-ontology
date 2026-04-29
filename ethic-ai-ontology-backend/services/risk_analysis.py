from db.neo4j_client import get_risk_from_graph

def analyze_text(text):
    return get_risk_from_graph(text.lower())