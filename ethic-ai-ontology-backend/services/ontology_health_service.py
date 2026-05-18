import logging
from db.connection import run_query

logger = logging.getLogger(__name__)

def get_ontology_health() -> dict:
    logger.info("Running ontology health validation...")
    
    # 1. Categories analysis
    category_query = """
    MATCH (c:AI_Category)
    OPTIONAL MATCH (c)-[:HAS_RISK]->(r:RiskLevel)
    OPTIONAL MATCH (c)-[:RELATED_TO_REGULATION]->(reg:Regulation)
    OPTIONAL MATCH (c)-[:IMPACTS_PRINCIPLE]->(p:EthicalPrinciple)
    OPTIONAL MATCH (k:Keyword)-[:MAPS_TO]->(c)
    RETURN 
        c.name AS category,
        count(DISTINCT r) AS risk_count,
        count(DISTINCT reg) AS regulation_count,
        count(DISTINCT p) AS principle_count,
        count(DISTINCT k) AS keyword_count
    """
    category_rows = run_query(category_query)
    
    total_categories = 0
    healthy_categories = 0
    incomplete_categories = []
    categories_without_keywords = []
    orphan_categories = []
    
    for row in category_rows:
        cat_name = row.get("category")
        if not cat_name:
            continue
            
        total_categories += 1
        missing = []
        if row["risk_count"] == 0:
            missing.append("HAS_RISK")
        if row["regulation_count"] == 0:
            missing.append("RELATED_TO_REGULATION")
        if row["principle_count"] == 0:
            missing.append("IMPACTS_PRINCIPLE")
            
        if row["keyword_count"] == 0:
            categories_without_keywords.append(cat_name)
            
        # An orphan category is one that has absolutely no relationships
        if row["risk_count"] == 0 and row["regulation_count"] == 0 and row["principle_count"] == 0 and row["keyword_count"] == 0:
            orphan_categories.append(cat_name)
            
        if not missing:
            healthy_categories += 1
        else:
            incomplete_categories.append({
                "category": cat_name,
                "missing": missing
            })
            
    # 2. Duplicated keywords (same term mapping to anything or multiple times)
    duplicate_kw_query = """
    MATCH (k:Keyword)
    WITH k.term AS term, count(k) AS occurrences
    WHERE occurrences > 1
    RETURN term, occurrences
    """
    dup_rows = run_query(duplicate_kw_query)
    duplicated_keywords = [
        {"term": r["term"], "occurrences": r["occurrences"]}
        for r in dup_rows if r.get("term")
    ]
    
    # 3. Disconnected nodes
    disconnected_query = """
    MATCH (n)
    WHERE (n:AI_Category OR n:Keyword OR n:RiskLevel OR n:Regulation OR n:EthicalPrinciple)
    AND NOT (n)--()
    RETURN labels(n) AS labels, coalesce(n.name, n.term, toString(id(n))) AS identifier
    """
    disc_rows = run_query(disconnected_query)
    disconnected_nodes = [
        {"labels": r["labels"], "identifier": r["identifier"]}
        for r in disc_rows
    ]
    
    # Completeness score
    completeness_score = 100.0
    if total_categories > 0:
        completeness_score = (healthy_categories / total_categories) * 100.0
        
    logger.info(f"Ontology health checked. Score: {completeness_score:.1f}%. {healthy_categories}/{total_categories} healthy categories.")
    
    return {
        "total_categories": total_categories,
        "healthy_categories": healthy_categories,
        "completeness_score": round(completeness_score, 2),
        "incomplete_categories": incomplete_categories,
        "categories_without_keywords": categories_without_keywords,
        "orphan_categories": orphan_categories,
        "duplicated_keywords": duplicated_keywords,
        "disconnected_nodes": disconnected_nodes
    }
