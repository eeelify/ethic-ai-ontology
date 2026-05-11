import logging

logger = logging.getLogger(__name__)

# Keyword mappings mapped to ontology entities
KEYWORD_RULES = {
    "hiring": {"system_type": "HiringAI", "risk_level": "HighRisk", "regulations": ["EU_AI_Act_Art_9", "GDPR_Art_22"]},
    "biometric": {"system_type": "BiometricSystem", "risk_level": "ProhibitedRisk", "regulations": ["EU_AI_Act_Art_5", "KVKK_Art_6", "GDPR_Art_9"]},
    "surveillance": {"system_type": "SurveillanceSystem", "risk_level": "ProhibitedRisk", "regulations": ["EU_AI_Act_Art_5"]},
    "healthcare": {"system_type": "HealthcareAI", "risk_level": "HighRisk", "regulations": ["GDPR_Art_9", "KVKK_Art_6"]},
    "personal data": {"system_type": "DataProcessingAI", "risk_level": "MediumRisk", "regulations": ["GDPR_Art_5", "KVKK_Art_4"]},
    "emotion recognition": {"system_type": "EmotionRecognitionAI", "risk_level": "ProhibitedRisk", "regulations": ["EU_AI_Act_Art_5"]}
}

def analyze_text(text: str) -> dict:
    logger.info("Analyzing text for keywords")
    t = text.lower()
    
    inferred_types = set()
    inferred_risks = set()
    inferred_regulations = set()
    
    for kw, data in KEYWORD_RULES.items():
        if kw in t:
            inferred_types.add(data["system_type"])
            inferred_risks.add(data["risk_level"])
            inferred_regulations.update(data["regulations"])
            
    return {
        "inferred_system_types": list(inferred_types),
        "inferred_risks": list(inferred_risks),
        "inferred_regulations": list(inferred_regulations)
    }
