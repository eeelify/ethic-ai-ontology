"""
OWL Ontoloji → Neo4j Aura Yükleyici
Kullanım: python load_to_neo4j.py
"""

from rdflib import Graph, RDF, OWL, RDFS, URIRef, Literal
from neo4j import GraphDatabase
import re

# ── BAĞLANTI BİLGİLERİNİ BURAYA GİR ─────────────────────────────────────────
URI      = "neo4j+s://ada522e9.databases.neo4j.io" # +ssc yerine +s daha sağlıklıdır
USER     = "ada522e9"
PASSWORD = "PaloXUBb0qARj_ZOPMKNWIE6Jo-RF612wta3ILZu9KM"
OWL_FILE = "EthicalAI_inferred.owl"

# Tek bir driver tanımı yapıyoruz
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
# ─────────────────────────────────────────────────────────────────────────────

WPS = "http://webprotege.stanford.edu/"
TAIR = "http://tair.adaptcentre.ie/ontologies/tair/"

def clean_name(uri):
    """IRI'den anlamlı isim çıkar"""
    uri = str(uri)
    for prefix in [WPS, TAIR, "http://www.w3.org/2002/07/owl#",
                   "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                   "http://tair.adaptcentre.ie/ontologies/tair"]:
        uri = uri.replace(prefix, "")
    uri = uri.lstrip("/# ")
    return uri if uri else "Unknown"

def get_label(g, uri):
    """rdfs:label varsa onu kullan, yoksa URI'den türet"""
    for label in g.objects(uri, RDFS.label):
        return str(label)
    return clean_name(uri)

print("OWL dosyası yükleniyor...")
g = Graph()
g.parse(OWL_FILE)
print(f"  {len(g)} triple yüklendi")

print("Neo4j'e bağlanılıyor...")


def load_ontology(tx, g):
    
    # 1. Tüm sınıfları OWLClass node olarak ekle
    classes_added = 0
    for cls in g.subjects(RDF.type, OWL.Class):
        if isinstance(cls, URIRef):
            name = get_label(g, cls)
            uri  = str(cls)
            tx.run("""
                MERGE (c:OWLClass {uri: $uri})
                SET c.name = $name
            """, uri=uri, name=name)
            classes_added += 1

    # 2. Named Individual'ları ekle
    individuals_added = 0
    for ind in g.subjects(RDF.type, OWL.NamedIndividual):
        if isinstance(ind, URIRef):
            name = get_label(g, ind)
            uri  = str(ind)
            # Sınıfını bul
            ind_classes = []
            for cls in g.objects(ind, RDF.type):
                if cls != OWL.NamedIndividual:
                    ind_classes.append(clean_name(cls))
            
            tx.run("""
                MERGE (i:Individual {uri: $uri})
                SET i.name = $name,
                    i.classes = $classes
            """, uri=uri, name=name, classes=ind_classes)
            individuals_added += 1

    # 3. SubClassOf ilişkilerini ekle
    subclass_added = 0
    for child, parent in g.subject_objects(RDFS.subClassOf):
        if isinstance(child, URIRef) and isinstance(parent, URIRef):
            tx.run("""
                MERGE (c:OWLClass {uri: $child_uri})
                SET c.name = $child_name
                MERGE (p:OWLClass {uri: $parent_uri})
                SET p.name = $parent_name
                MERGE (c)-[:SUBCLASS_OF]->(p)
            """, 
                child_uri=str(child),   child_name=get_label(g, child),
                parent_uri=str(parent), parent_name=get_label(g, parent)
            )
            subclass_added += 1

    # 4. Object property assertion'larını ekle (en kritik kısım)
    props_added = 0
    
    # Önemli property'lerin IRI'ları
    important_props = {
        f"{WPS}hasRiskLevel":              "HAS_RISK_LEVEL",
        f"{WPS}requires":                  "REQUIRES",
        f"{WPS}violates":                  "VIOLATES",
        f"{WPS}conflictsWith":             "CONFLICTS_WITH",
        f"{WPS}affects":                   "AFFECTS",
        f"{WPS}hasSector":                 "HAS_SECTOR",
        f"{WPS}hasDecisionType":           "HAS_DECISION_TYPE",
        f"{WPS}hasAutomationLevel":        "HAS_AUTOMATION_LEVEL",
        f"{WPS}hasUserArea":               "HAS_USER_AREA",
        f"{WPS}hasLegalBasis":             "HAS_LEGAL_BASIS",
        f"{WPS}hasEthicalTension":         "HAS_ETHICAL_TENSION",
        f"{WPS}isViolatedBy":              "IS_VIOLATED_BY",
        f"{WPS}hasRiskLevel":              "HAS_RISK_LEVEL",
        f"{WPS}mitigates":                 "MITIGATES",
        f"{WPS}isGovernedBy":              "IS_GOVERNED_BY",
        f"{WPS}processes":                 "PROCESSES",
        f"{WPS}transfersTo":               "TRANSFERS_TO",
    }
    
    for prop_uri, rel_type in important_props.items():
        prop = URIRef(prop_uri)
        for subj, obj in g.subject_objects(prop):
            if isinstance(subj, URIRef) and isinstance(obj, URIRef):
                tx.run(f"""
                    MERGE (s:Individual {{uri: $subj_uri}})
                    SET s.name = $subj_name
                    MERGE (o:Individual {{uri: $obj_uri}})
                    SET o.name = $obj_name
                    MERGE (s)-[:{rel_type}]->(o)
                """,
                    subj_uri=str(subj),  subj_name=get_label(g, subj),
                    obj_uri=str(obj),    obj_name=get_label(g, obj)
                )
                props_added += 1

    # 5. ClassAssertion: Individual → OWLClass bağlantısı
    type_added = 0
    for ind, cls in g.subject_objects(RDF.type):
        if (isinstance(ind, URIRef) and isinstance(cls, URIRef) and 
            cls not in [OWL.NamedIndividual, OWL.Class, RDF.type]):
            tx.run("""
                MERGE (i:Individual {uri: $ind_uri})
                SET i.name = $ind_name
                MERGE (c:OWLClass {uri: $cls_uri})
                SET c.name = $cls_name
                MERGE (i)-[:INSTANCE_OF]->(c)
            """,
                ind_uri=str(ind),   ind_name=get_label(g, ind),
                cls_uri=str(cls),   cls_name=get_label(g, cls)
            )
            type_added += 1

    return classes_added, individuals_added, subclass_added, props_added, type_added

print("Veriler Neo4j'e yazılıyor...")
with driver.session() as session:
    # Önce temizle
    session.run("MATCH (n) DETACH DELETE n")
    print("  Eski veriler temizlendi")
    
    results = session.execute_write(load_ontology, g)
    c, i, s, p, t = results
    print(f"  ✓ {c} sınıf node")
    print(f"  ✓ {i} individual node")
    print(f"  ✓ {s} SUBCLASS_OF ilişkisi")
    print(f"  ✓ {p} property assertion ilişkisi")
    print(f"  ✓ {t} INSTANCE_OF ilişkisi")

driver.close()
print("\n✅ Neo4j yükleme tamamlandı!")
print("\nTest sorguları (Neo4j Query'de çalıştır):")
print("""
-- Risk seviyeleri:
MATCH (s:Individual)-[:HAS_RISK_LEVEL]->(r:Individual)
RETURN s.name, r.name

-- Etik ihlaller:
MATCH (s:Individual)-[:VIOLATES]->(p:Individual)
RETURN s.name AS sistem, p.name AS ihlal_edilen_ilke

-- Etik gerilim döngüleri:
MATCH p=(a:Individual)-[:CONFLICTS_WITH*2..4]->(a)
RETURN p LIMIT 5
""")
