from dotenv import load_dotenv
load_dotenv()
from db.connection import run_query

res = run_query("""
MATCH (s:Individual)-[:INSTANCE_OF]->(c {name: 'BiometricIdentificationSystem'})
RETURN s.name, [(s)-[r]->(t) | type(r)] as rels
""")
print(res)
