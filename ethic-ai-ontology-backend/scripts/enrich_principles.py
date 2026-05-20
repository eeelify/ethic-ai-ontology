import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to sys.path so we can import from db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import get_session

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("enrichment.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Predefined mappings based on category semantics
MAPPINGS = {
    "biometric": ["Privacy", "DataProtection", "HumanAgency", "Autonomy", "NonDiscrimination"],
    "surveillance": ["Privacy", "Transparency", "Accountability", "HumanAgency"],
    "healthcare": ["Safety", "Accountability", "HumanOversight", "Transparency"],
    "creditscoring": ["Fairness", "NonDiscrimination", "Explainability", "Accountability"],
    "educational": ["Fairness", "Transparency", "HumanOversight", "Autonomy"]
}

# Default templates for relationship properties
DEFAULTS = {
    "Privacy": {"severity": "Critical", "harm_type": "Privacy Violation"},
    "Fairness": {"severity": "High", "harm_type": "Discrimination"},
    "Transparency": {"severity": "Medium", "harm_type": "Opacity"},
    "Autonomy": {"severity": "High", "harm_type": "Autonomy Erosion"},
    "Accountability": {"severity": "High", "harm_type": "Accountability Gap"},
    "Explainability": {"severity": "Medium", "harm_type": "Lack of Explainability"},
    "HumanAgency": {"severity": "High", "harm_type": "Loss of Agency"},
    "DataProtection": {"severity": "Critical", "harm_type": "Data Breach Risk"},
    "Safety": {"severity": "High", "harm_type": "Security Risk"},
    "HumanOversight": {"severity": "High", "harm_type": "System Error"},
    "NonDiscrimination": {"severity": "High", "harm_type": "Bias"}
}

def detect_category_type(name: str) -> str:
    """Returns the matching keyword if the name contains it, otherwise None."""
    name_lower = name.lower()
    for key in MAPPINGS.keys():
        if key in name_lower:
            return key
    return None

def enrich_principles():
    logger.info("Starting Ontology Enrichment for Ethical Principles...")

    # Query to find all AI_Category nodes so we can update or create relations
    query_categories = """
    MATCH (c:AI_Category)
    RETURN c.name AS name
    """

    enrich_query = """
    MATCH (c:AI_Category {name: $category_name})
    MERGE (p:EthicalPrinciple {name: $principle})
    MERGE (c)-[r:IMPACTS_PRINCIPLE]->(p)
    SET 
        r.reason = $reason,
        r.impact = $impact,
        r.severity = $severity,
        r.harm_type = $harm_type
    RETURN r
    """

    enriched_count = 0
    skipped_count = 0

    with get_session() as session:
        # 1. Fetch categories
        result = session.run(query_categories)
        categories = [record.data() for record in result]
        
        if not categories:
            logger.info("No AI_Category nodes found. Ontology might be empty.")
            return

        logger.info(f"Found {len(categories)} categories to evaluate for enrichment.")

        # 2. Process each category
        for cat in categories:
            cat_name = cat.get("name")
            
            cat_type = detect_category_type(cat_name)
            if not cat_type:
                logger.info(f"Skipping category '{cat_name}': No matching semantic mapping found.")
                skipped_count += 1
                continue

            principles = MAPPINGS[cat_type]
            logger.info(f"Enriching category '{cat_name}' with principles: {principles}")

            for principle in principles:
                props = DEFAULTS.get(principle, {
                    "severity": "Unknown",
                    "harm_type": "Unknown"
                })
                
                # Dynamically generate reason and impact based on semantics
                reason = f"Potential {props['harm_type'].lower()} in {cat_name} systems."
                impact = f"Impacts the {principle.lower()} of individuals subjected to {cat_type} technology."
                
                # Execute merge query
                session.run(enrich_query, {
                    "category_name": cat_name,
                    "principle": principle,
                    "reason": reason,
                    "impact": impact,
                    "severity": props["severity"],
                    "harm_type": props["harm_type"]
                })
                logger.info(f" -> Created relationship to principle: {principle}")
            
            enriched_count += 1

    logger.info("Enrichment process completed.")
    logger.info(f"Total categories enriched: {enriched_count}")
    logger.info(f"Total categories skipped: {skipped_count}")

if __name__ == "__main__":
    enrich_principles()
