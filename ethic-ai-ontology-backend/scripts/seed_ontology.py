"""
seed_ontology.py  –  run: python scripts/seed_ontology.py
Graph model:
  (:Keyword {term})-[:MAPS_TO]->(:AI_Category {name, risk_level})
  (:AI_Category)-[:HAS_REGULATION]->(:Regulation {name})
  (:AI_Category)-[r:MAY_VIOLATE {reason,impact,severity,harm_type}]->(:EthicalPrinciple {name})
All MERGE statements → idempotent / safe to re-run.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(override=True)
from db.connection import get_session

# ── helper ────────────────────────────────────────────────────────────────────
def V(principle, reason, impact, severity, harm_type):
    return {"principle": principle, "reason": reason,
            "impact": impact, "severity": severity, "harm_type": harm_type}

# ── 1. CATEGORIES ─────────────────────────────────────────────────────────────
CATEGORIES = [
  {
    "name": "HiringAI", "risk_level": "HighRisk",
    "regulations": ["EU_AI_Act_Art_9","EU_AI_Act_Art_10","GDPR_Art_22","GDPR_Art_5","KVKK_Art_4"],
    "violations": [
      V("Fairness","Automated hiring may encode historical demographic biases","Unequal evaluation of candidates from underrepresented groups","High","Discrimination"),
      V("NonDiscrimination","Models trained on biased data may filter protected groups","Systematic exclusion based on gender, ethnicity, or age","High","Discrimination"),
      V("Transparency","Opaque scoring models obscure rejection reasons","Applicants cannot understand or contest decisions","Medium","Opacity"),
      V("Accountability","Automated decisions may lack identifiable human responsibility","No clear party accountable for unfair outcomes","High","Accountability Gap"),
      V("Explainability","Black-box models cannot justify individual hiring decisions","Candidates receive no meaningful explanation of rejection","Medium","Lack of Explainability"),
      V("HumanOversight","Full automation may remove human judgment from hiring","High-stakes decisions made without human review","High","Automation Risk"),
    ]
  },
  {
    "name": "BiometricAI", "risk_level": "ProhibitedRisk",
    "regulations": ["EU_AI_Act_Art_5","GDPR_Art_9","KVKK_Art_6","EU_AI_Act_Art_10"],
    "violations": [
      V("Privacy","Biometric collection is inherently invasive and hard to anonymize","Permanent exposure of immutable personal characteristics","Critical","Privacy Violation"),
      V("DataProtection","Biometric templates stored in DBs create high-value breach targets","Irreversible identity exposure if databases are compromised","Critical","Data Breach Risk"),
      V("HumanAgency","Biometric systems can operate without explicit individual consent","Individuals cannot opt out of identification in public spaces","High","Loss of Agency"),
      V("Autonomy","Continuous biometric monitoring erodes individual freedom","Chilling effect on behaviour and self-expression","High","Autonomy Erosion"),
      V("NonDiscrimination","Biometric systems have lower accuracy for certain demographic groups","Higher false positive/negative rates for darker skin tones","High","Algorithmic Bias"),
      V("Safety","Spoofing attacks can compromise biometric authentication","Security failures enabling unauthorised access or false identification","High","Security Risk"),
    ]
  },
  {
    "name": "SurveillanceAI", "risk_level": "ProhibitedRisk",
    "regulations": ["EU_AI_Act_Art_5","GDPR_Art_6","KVKK_Art_5"],
    "violations": [
      V("Privacy","Mass surveillance collects data without individual knowledge","Pervasive monitoring of private behaviour and movements","Critical","Privacy Violation"),
      V("HumanAgency","Surveillance operates without individual consent or notification","People cannot control how they are monitored","High","Loss of Agency"),
      V("Autonomy","Constant surveillance causes behavioural self-censorship","Suppression of free expression and lawful behaviour","High","Autonomy Erosion"),
      V("Accountability","Surveillance data use may not be audited or overseen","Misuse of surveillance data without accountability","High","Accountability Gap"),
      V("Transparency","Surveillance systems are often deployed covertly","Public unaware of monitoring scope and data retention","High","Opacity"),
    ]
  },
  {
    "name": "EmotionRecognitionAI", "risk_level": "ProhibitedRisk",
    "regulations": ["EU_AI_Act_Art_5","GDPR_Art_9","KVKK_Art_6"],
    "violations": [
      V("Privacy","Emotion recognition captures psychological states without consent","Involuntary disclosure of mental health and emotional conditions","Critical","Privacy Violation"),
      V("HumanAgency","Emotional states inferred without knowledge or consent","Individuals cannot control emotional profiling","High","Loss of Agency"),
      V("Autonomy","Workplace emotion AI may coerce employees to mask genuine feelings","Suppression of authentic emotional expression","High","Autonomy Erosion"),
      V("NonDiscrimination","Emotion recognition has poor cross-cultural accuracy","Misclassification based on cultural norms or neurodivergence","High","Algorithmic Bias"),
      V("Transparency","Emotion recognition systems are rarely disclosed to subjects","Hidden psychological profiling without subject awareness","High","Opacity"),
      V("Explainability","Emotion classification models cannot reliably explain predictions","No meaningful justification for assigned emotional labels","Medium","Lack of Explainability"),
    ]
  },
  {
    "name": "HealthcareAI", "risk_level": "HighRisk",
    "regulations": ["EU_AI_Act_Art_9","GDPR_Art_9","KVKK_Art_6","EU_AI_Act_Art_13","EU_AI_Act_Art_14"],
    "violations": [
      V("Safety","Incorrect medical AI predictions can cause harmful treatment","Patient harm from misdiagnosis or inappropriate treatment","Critical","Physical Harm"),
      V("Trustworthiness","Healthcare AI may perform poorly on distribution-shifted populations","Unreliable predictions for underrepresented patient groups","High","Reliability Risk"),
      V("Accountability","Distributed responsibility creates accountability gaps","Unclear liability when AI-assisted decisions cause harm","High","Accountability Gap"),
      V("Transparency","Clinical AI may not expose its decision-making process","Clinicians cannot assess whether AI reasoning is sound","High","Opacity"),
      V("HumanOversight","Over-reliance on AI reduces clinician vigilance","Medical errors from automation bias","High","Automation Risk"),
      V("DataProtection","Healthcare AI requires large sensitive health datasets","Risk of health data misuse or unauthorised access","Critical","Data Breach Risk"),
      V("Privacy","AI systems trained on patient data may leak health information","Exposure of sensitive medical history through model outputs","High","Privacy Violation"),
    ]
  },
  {
    "name": "CreditScoringAI", "risk_level": "HighRisk",
    "regulations": ["EU_AI_Act_Art_9","GDPR_Art_22","GDPR_Art_5","KVKK_Art_4"],
    "violations": [
      V("Fairness","Credit models may perpetuate historical lending discrimination","Unfair loan rejections for marginalised communities","High","Discrimination"),
      V("NonDiscrimination","Proxy variables can encode protected characteristics","Discrimination via zip code, race, or gender proxies","High","Algorithmic Bias"),
      V("Transparency","Credit scoring algorithms are often proprietary black boxes","Consumers cannot understand why they were denied credit","High","Opacity"),
      V("Explainability","Complex ML models cannot provide legally required explanations","Violation of right to explanation under GDPR Art. 22","High","Lack of Explainability"),
      V("Accountability","Automated credit decisions may lack meaningful human review","No recourse for consumers facing unfair automated decisions","High","Accountability Gap"),
      V("HumanOversight","Fully automated credit pipelines remove human judgment","Systemic errors propagate without human correction","Medium","Automation Risk"),
    ]
  },
  {
    "name": "EducationalAI", "risk_level": "HighRisk",
    "regulations": ["EU_AI_Act_Art_9","GDPR_Art_22","GDPR_Art_5","KVKK_Art_4"],
    "violations": [
      V("Fairness","Educational AI may reflect biases in historical academic data","Unequal learning opportunities for disadvantaged students","High","Discrimination"),
      V("NonDiscrimination","Automated grading may disadvantage non-native speakers","Systematic undervaluation of certain student groups","High","Algorithmic Bias"),
      V("HumanAgency","Adaptive systems constrain curriculum paths algorithmically","Students lose control over their own learning journey","Medium","Loss of Agency"),
      V("Transparency","Students may not understand how AI grades or recommends content","Black-box educational decisions undermine trust","Medium","Opacity"),
      V("Accountability","AI-driven academic decisions lack clear human accountability","Unclear responsibility when AI contributes to academic failures","High","Accountability Gap"),
      V("Autonomy","AI-based proctoring imposes invasive monitoring on students","Erosion of student autonomy during examinations","High","Autonomy Erosion"),
    ]
  },
  {
    "name": "LawEnforcementAI", "risk_level": "ProhibitedRisk",
    "regulations": ["EU_AI_Act_Art_5","EU_AI_Act_Art_6","GDPR_Art_9","KVKK_Art_6"],
    "violations": [
      V("Fairness","Predictive policing may unfairly target communities based on historical over-policing","Racially biased enforcement of minority communities","Critical","Discrimination"),
      V("NonDiscrimination","Historical crime data encodes systemic racial biases","Disproportionate surveillance and arrest of minority groups","Critical","Algorithmic Bias"),
      V("Accountability","Automated law enforcement decisions are difficult to challenge legally","Individuals face consequences from opaque AI without recourse","Critical","Accountability Gap"),
      V("HumanOversight","Over-reliance on AI reduces human judgment in policing","Consequential decisions made without human review","High","Automation Risk"),
      V("Transparency","Predictive policing algorithms are rarely disclosed to communities","Communities cannot assess or challenge AI-driven enforcement","High","Opacity"),
      V("Safety","False positives in threat detection can endanger innocents","Wrongful stops, arrests, or use of force from AI errors","Critical","Physical Harm"),
      V("Privacy","Law enforcement AI aggregates extensive personal data for surveillance","Mass profiling of individuals in daily lives","High","Privacy Violation"),
    ]
  },
  {
    "name": "RecommendationAI", "risk_level": "LimitedRisk",
    "regulations": ["GDPR_Art_5","GDPR_Art_22","EU_AI_Act_Art_52","KVKK_Art_4"],
    "violations": [
      V("Transparency","Recommendation algorithms are not disclosed to users","Users unaware of how content is curated and prioritised","Medium","Opacity"),
      V("Autonomy","Filter bubbles limit exposure to diverse content","Reinforcement of existing beliefs and polarisation","Medium","Autonomy Erosion"),
      V("HumanAgency","Recommendation systems can manipulate user attention","Reduced ability to make independent content choices","Medium","Manipulation"),
      V("DataProtection","Recommendation systems require extensive behavioural data","Personal preference data used without explicit understanding","Medium","Data Misuse"),
    ]
  },
  {
    "name": "GenerativeAI", "risk_level": "LimitedRisk",
    "regulations": ["EU_AI_Act_Art_52","EU_AI_Act_Art_53","GDPR_Art_5"],
    "violations": [
      V("Transparency","Generative AI outputs may be indistinguishable from human content","Users deceived about the nature and origin of AI content","High","Deception"),
      V("Trustworthiness","LLMs can generate factually incorrect information confidently","Hallucinated information presented as factual causing misinformation","High","Misinformation"),
      V("Accountability","Attribution of harmful AI-generated content is difficult","Creators of harmful deepfakes may evade accountability","High","Accountability Gap"),
      V("Explainability","Generative AI cannot reliably explain why it produces outputs","Inability to audit or verify the reasoning behind generated content","Medium","Lack of Explainability"),
      V("Safety","Generative AI can be misused to produce harmful content at scale","Large-scale production of misinformation or illegal content","High","Societal Harm"),
      V("HumanOversight","Automated content pipelines may operate without human review","Harmful content published without human gatekeeping","High","Automation Risk"),
    ]
  },
  {
    "name": "ProfilingAI", "risk_level": "HighRisk",
    "regulations": ["GDPR_Art_22","GDPR_Art_5","GDPR_Art_9","EU_AI_Act_Art_9","KVKK_Art_4","KVKK_Art_6"],
    "violations": [
      V("Privacy","Profiling infers sensitive attributes not directly disclosed","Exposure of inferred sensitive characteristics like health or politics","High","Privacy Violation"),
      V("DataProtection","Profiling often processes special category data indirectly","Sensitive data processing without explicit legal basis","High","Data Misuse"),
      V("Autonomy","Pervasive profiling constrains individual behaviour","Chilling effect on personal expression and online behaviour","Medium","Autonomy Erosion"),
      V("NonDiscrimination","Profiles built from biased data lead to discriminatory treatment","Different service quality or pricing based on demographic profiles","High","Discrimination"),
      V("HumanAgency","Individuals have little control over how profiles are built","Loss of control over personal digital identity","High","Loss of Agency"),
      V("Transparency","Profiling systems rarely disclose the scope of data collection","Users unaware of the extent of profiling activities","High","Opacity"),
    ]
  },
  {
    "name": "SocialScoringAI", "risk_level": "ProhibitedRisk",
    "regulations": ["EU_AI_Act_Art_5","GDPR_Art_22","KVKK_Art_4"],
    "violations": [
      V("Fairness","Social scoring applies uniform metrics to complex human behaviours","Reductive and unfair assessment of individual worth","Critical","Discrimination"),
      V("NonDiscrimination","Social scores may encode socioeconomic and cultural biases","Systematic disadvantaging of marginalised communities","Critical","Algorithmic Bias"),
      V("HumanAgency","Social scoring creates pervasive behavioural control","Individuals constrained to conform to state or corporate preferences","Critical","Loss of Agency"),
      V("Autonomy","Fear of negative scoring eliminates genuine freedom of expression","Complete erosion of individual autonomy in scored societies","Critical","Autonomy Erosion"),
      V("Privacy","Social scoring requires continuous monitoring of all aspects of life","Total surveillance of private and public behaviour","Critical","Privacy Violation"),
      V("Accountability","Score criteria and weighting are rarely transparent or challengeable","Individuals cannot contest scores that determine life opportunities","Critical","Accountability Gap"),
      V("Trustworthiness","Social scoring systems can be gamed or manipulated by power","Corrupt scoring outcomes that undermine social trust","High","Systemic Corruption"),
    ]
  },
]

# ── 2. KEYWORDS ───────────────────────────────────────────────────────────────
KEYWORDS = [
    # HiringAI
    ("cv","HiringAI"),("resume","HiringAI"),("recruitment","HiringAI"),
    ("hiring","HiringAI"),("job applicant","HiringAI"),("candidate screening","HiringAI"),
    ("applicant tracking","HiringAI"),("talent acquisition","HiringAI"),
    ("automated interview","HiringAI"),("employment decision","HiringAI"),
    ("workforce selection","HiringAI"),("candidate scoring","HiringAI"),
    ("job screening","HiringAI"),("staff selection","HiringAI"),
    # BiometricAI
    ("biometric","BiometricAI"),("fingerprint","BiometricAI"),
    ("face recognition","BiometricAI"),("facial recognition","BiometricAI"),
    ("iris scan","BiometricAI"),("retina scan","BiometricAI"),
    ("voice recognition","BiometricAI"),("gait analysis","BiometricAI"),
    ("palm vein","BiometricAI"),("biometric identification","BiometricAI"),
    ("biometric authentication","BiometricAI"),("biometric verification","BiometricAI"),
    ("identity verification","BiometricAI"),
    # SurveillanceAI
    ("surveillance","SurveillanceAI"),("cctv","SurveillanceAI"),
    ("mass monitoring","SurveillanceAI"),("real-time monitoring","SurveillanceAI"),
    ("behavior tracking","SurveillanceAI"),("location tracking","SurveillanceAI"),
    ("crowd monitoring","SurveillanceAI"),("public monitoring","SurveillanceAI"),
    ("remote monitoring","SurveillanceAI"),("activity surveillance","SurveillanceAI"),
    ("employee monitoring","SurveillanceAI"),("movement tracking","SurveillanceAI"),
    # EmotionRecognitionAI
    ("emotion recognition","EmotionRecognitionAI"),("emotion detection","EmotionRecognitionAI"),
    ("sentiment analysis","EmotionRecognitionAI"),("affect detection","EmotionRecognitionAI"),
    ("mood detection","EmotionRecognitionAI"),("facial expression","EmotionRecognitionAI"),
    ("emotional state","EmotionRecognitionAI"),("emotion ai","EmotionRecognitionAI"),
    ("emotion classification","EmotionRecognitionAI"),("affective computing","EmotionRecognitionAI"),
    # HealthcareAI
    ("healthcare","HealthcareAI"),("medical diagnosis","HealthcareAI"),
    ("clinical decision","HealthcareAI"),("patient monitoring","HealthcareAI"),
    ("medical imaging","HealthcareAI"),("drug discovery","HealthcareAI"),
    ("treatment recommendation","HealthcareAI"),("disease prediction","HealthcareAI"),
    ("radiology ai","HealthcareAI"),("electronic health record","HealthcareAI"),
    ("ehr","HealthcareAI"),("hospital ai","HealthcareAI"),
    ("health risk assessment","HealthcareAI"),("symptom checker","HealthcareAI"),
    ("telemedicine","HealthcareAI"),
    # CreditScoringAI
    ("credit scoring","CreditScoringAI"),("credit assessment","CreditScoringAI"),
    ("loan decision","CreditScoringAI"),("loan approval","CreditScoringAI"),
    ("creditworthiness","CreditScoringAI"),("financial risk scoring","CreditScoringAI"),
    ("lending decision","CreditScoringAI"),("insurance scoring","CreditScoringAI"),
    ("fraud detection","CreditScoringAI"),("risk scoring","CreditScoringAI"),
    ("underwriting","CreditScoringAI"),("payment risk","CreditScoringAI"),
    # EducationalAI
    ("educational","EducationalAI"),("student assessment","EducationalAI"),
    ("learning platform","EducationalAI"),("adaptive learning","EducationalAI"),
    ("exam proctoring","EducationalAI"),("automated grading","EducationalAI"),
    ("grade prediction","EducationalAI"),("student performance","EducationalAI"),
    ("tutoring system","EducationalAI"),("learning analytics","EducationalAI"),
    ("dropout prediction","EducationalAI"),("e-learning","EducationalAI"),
    ("school ai","EducationalAI"),
    # LawEnforcementAI
    ("law enforcement","LawEnforcementAI"),("predictive policing","LawEnforcementAI"),
    ("crime prediction","LawEnforcementAI"),("recidivism prediction","LawEnforcementAI"),
    ("threat detection","LawEnforcementAI"),("border control","LawEnforcementAI"),
    ("suspect identification","LawEnforcementAI"),("judicial decision","LawEnforcementAI"),
    ("parole decision","LawEnforcementAI"),("criminal justice","LawEnforcementAI"),
    ("sentencing ai","LawEnforcementAI"),("police ai","LawEnforcementAI"),
    # RecommendationAI
    ("recommendation","RecommendationAI"),("content recommendation","RecommendationAI"),
    ("product recommendation","RecommendationAI"),("personalized content","RecommendationAI"),
    ("news feed","RecommendationAI"),("collaborative filtering","RecommendationAI"),
    ("content filtering","RecommendationAI"),("targeted advertising","RecommendationAI"),
    ("search ranking","RecommendationAI"),("social media algorithm","RecommendationAI"),
    ("streaming recommendation","RecommendationAI"),
    # GenerativeAI
    ("generative ai","GenerativeAI"),("large language model","GenerativeAI"),
    ("llm","GenerativeAI"),("text generation","GenerativeAI"),
    ("image generation","GenerativeAI"),("deepfake","GenerativeAI"),
    ("synthetic media","GenerativeAI"),("gpt","GenerativeAI"),
    ("chatbot","GenerativeAI"),("ai-generated content","GenerativeAI"),
    ("diffusion model","GenerativeAI"),("foundation model","GenerativeAI"),
    ("prompt engineering","GenerativeAI"),
    # ProfilingAI
    ("profiling","ProfilingAI"),("user profiling","ProfilingAI"),
    ("behavioral profiling","ProfilingAI"),("data profiling","ProfilingAI"),
    ("personal data","ProfilingAI"),("demographic profiling","ProfilingAI"),
    ("consumer profiling","ProfilingAI"),("online tracking","ProfilingAI"),
    ("digital footprint","ProfilingAI"),("audience segmentation","ProfilingAI"),
    ("microtargeting","ProfilingAI"),("psychographic profiling","ProfilingAI"),
    # SocialScoringAI
    ("social scoring","SocialScoringAI"),("social credit","SocialScoringAI"),
    ("citizen scoring","SocialScoringAI"),("trustworthiness score","SocialScoringAI"),
    ("behavior scoring","SocialScoringAI"),("reputation scoring","SocialScoringAI"),
    ("social ranking","SocialScoringAI"),("individual scoring","SocialScoringAI"),
    ("social monitoring","SocialScoringAI"),
]

# ── Cypher ────────────────────────────────────────────────────────────────────
_CAT_CYPHER = """
MERGE (cat:AI_Category {name: $name})
  ON CREATE SET cat.risk_level = $risk_level
  ON MATCH  SET cat.risk_level = $risk_level
WITH cat
MERGE (r:RiskLevel {name: $risk_level})
MERGE (cat)-[:HAS_RISK]->(r)
WITH cat
UNWIND $regulations AS reg_name
  MERGE (reg:Regulation {name: reg_name})
  MERGE (cat)-[:RELATED_TO_REGULATION]->(reg)
  MERGE (cat)-[:HAS_REGULATION]->(reg)
"""

_VIOLATION_CYPHER = """
MATCH (cat:AI_Category {name: $category})
MERGE (ep:EthicalPrinciple {name: $principle})
MERGE (cat)-[r:IMPACTS_PRINCIPLE]->(ep)
SET r.reason    = $reason,
    r.impact    = $impact,
    r.severity  = $severity,
    r.harm_type = $harm_type
WITH cat, ep
MERGE (cat)-[old_r:MAY_VIOLATE]->(ep)
SET old_r.reason    = $reason,
    old_r.impact    = $impact,
    old_r.severity  = $severity,
    old_r.harm_type = $harm_type
"""

_KW_CYPHER = """
MERGE (kw:Keyword {term: $term})
MERGE (cat:AI_Category {name: $category})
MERGE (kw)-[:MAPS_TO]->(cat)
"""


def seed():
    with get_session() as session:
        print("Seeding categories + regulations...")
        for cat in CATEGORIES:
            session.run(_CAT_CYPHER, name=cat["name"],
                        risk_level=cat["risk_level"],
                        regulations=cat["regulations"])
            print(f"  [CAT] {cat['name']} ({cat['risk_level']}, {len(cat['regulations'])} regs)")

        print("\nSeeding MAY_VIOLATE relationships with ethical metadata...")
        for cat in CATEGORIES:
            for v in cat["violations"]:
                session.run(_VIOLATION_CYPHER,
                            category=cat["name"],
                            principle=v["principle"],
                            reason=v["reason"],
                            impact=v["impact"],
                            severity=v["severity"],
                            harm_type=v["harm_type"])
            print(f"  [ETH] {cat['name']} -> {len(cat['violations'])} violations")

        print("\nSeeding keywords...")
        for term, category in KEYWORDS:
            session.run(_KW_CYPHER, term=term, category=category)
            print(f"  [KW]  '{term}' -> {category}")

    total_violations = sum(len(c["violations"]) for c in CATEGORIES)
    print(f"\nDone. {len(CATEGORIES)} categories | {total_violations} ethical violations | {len(KEYWORDS)} keywords.")


if __name__ == "__main__":
    seed()
