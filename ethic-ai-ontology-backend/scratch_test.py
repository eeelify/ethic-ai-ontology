from dotenv import load_dotenv
load_dotenv(override=True)
from db.connection import run_query

print("--- Relationships for AmazonHR_CVFilter ---")
res = run_query("""
MATCH (s:Individual {name: 'AmazonHR_CVFilter'})-[r]->(t)
RETURN type(r) as type, labels(t) as labels, t.name as name, properties(t) as props
""")
for r in res:
    print(f"Relationship: {r['type']} -> Labels: {r['labels']}, Name: {r['name']}")
    print(f"  Target Props: {r['props']}")



