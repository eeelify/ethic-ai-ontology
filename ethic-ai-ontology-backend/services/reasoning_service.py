import logging
from owlready2 import *
import uuid

logger = logging.getLogger(__name__)

# Create an in-memory ontology for reasoning
onto = get_ontology("http://ethic-ai.org/ontology.owl")

with onto:
    # --- Base Classes ---
    class AISystem(Thing): pass
    
    # --- Initial Risk Classes ---
    class InitialProhibitedRisk(AISystem): pass
    class InitialHighRisk(AISystem): pass
    class InitialLimitedRisk(AISystem): pass
    class InitialMinimalRisk(AISystem): pass
    
    # --- Final/Mitigation Classes ---
    class MitigatedRiskSystem(AISystem): pass
    class UnmitigatedRiskSystem(AISystem): pass
    
    # --- Risk Triggers ---
    class RiskTrigger(Thing): pass
    class BiometricFeature(RiskTrigger): pass
    class EmotionRecognitionFeature(RiskTrigger): pass
    class ProfilingFeature(RiskTrigger): pass
    class AutomatedDecisionFeature(RiskTrigger): pass
    class SurveillanceFeature(RiskTrigger): pass
    class HiringFeature(RiskTrigger): pass
    class CreditScoringFeature(RiskTrigger): pass
    class EducationalAssessmentFeature(RiskTrigger): pass
    class HealthcareFeature(RiskTrigger): pass
    
    # --- Data Types ---
    class ProcessedData(Thing): pass
    class SensitiveHealthData(ProcessedData): pass
    class CriminalData(ProcessedData): pass
    class BiometricData(ProcessedData): pass
    
    # --- Safeguards ---
    class Safeguard(Thing): pass
    class LegalBasis(Safeguard): pass
    class ExplicitConsent(Safeguard): pass
    class HumanOversight(Safeguard): pass
    class DataMinimization(Safeguard): pass
    class Anonymization(Safeguard): pass
    class Pseudonymization(Safeguard): pass
    class PurposeLimitation(Safeguard): pass
    class SecurityMeasure(Safeguard): pass
    class TransparencyMeasure(Safeguard): pass
    class ExplainabilityMeasure(Safeguard): pass
    class ComplianceProcedure(Safeguard): pass
    
    # --- Properties ---
    class hasRiskTrigger(ObjectProperty):
        domain = [AISystem]
        range = [RiskTrigger]
        
    class processesData(ObjectProperty):
        domain = [AISystem]
        range = [ProcessedData]
        
    class hasSafeguard(ObjectProperty):
        domain = [AISystem]
        range = [Safeguard]

    # --- SWRL RULES: INITIAL RISK EVALUATION ---
    
    # Prohibited Triggers
    r_init_1 = Imp()
    r_init_1.set_as_rule("AISystem(?a), hasRiskTrigger(?a, ?t), SurveillanceFeature(?t) -> InitialProhibitedRisk(?a)")
    
    r_init_2 = Imp()
    r_init_2.set_as_rule("AISystem(?a), hasRiskTrigger(?a, ?t), EmotionRecognitionFeature(?t) -> InitialProhibitedRisk(?a)")
    
    r_init_3 = Imp() # Biometric is prohibited by default unless mitigated
    r_init_3.set_as_rule("AISystem(?a), hasRiskTrigger(?a, ?t), BiometricFeature(?t) -> InitialProhibitedRisk(?a)")
    
    # High Risk Triggers
    r_init_4 = Imp()
    r_init_4.set_as_rule("AISystem(?a), hasRiskTrigger(?a, ?t), HiringFeature(?t) -> InitialHighRisk(?a)")
    
    r_init_5 = Imp()
    r_init_5.set_as_rule("AISystem(?a), hasRiskTrigger(?a, ?t), CreditScoringFeature(?t) -> InitialHighRisk(?a)")
    
    r_init_6 = Imp()
    r_init_6.set_as_rule("AISystem(?a), hasRiskTrigger(?a, ?t), EducationalAssessmentFeature(?t) -> InitialHighRisk(?a)")
    
    r_init_7 = Imp()
    r_init_7.set_as_rule("AISystem(?a), hasRiskTrigger(?a, ?t), HealthcareFeature(?t) -> InitialHighRisk(?a)")
    
    r_init_8 = Imp()
    r_init_8.set_as_rule("AISystem(?a), hasRiskTrigger(?a, ?t), ProfilingFeature(?t) -> InitialHighRisk(?a)")
    
    # --- SWRL RULES: MITIGATION (CONTEXT AWARE) ---
    
    # Mitigation 1: Biometric + Legal Basis + Consent -> Mitigated
    r_mit_1 = Imp()
    r_mit_1.set_as_rule("InitialProhibitedRisk(?a), hasRiskTrigger(?a, ?t), BiometricFeature(?t), hasSafeguard(?a, ?s1), LegalBasis(?s1), hasSafeguard(?a, ?s2), ExplicitConsent(?s2) -> MitigatedRiskSystem(?a)")
    
    # Mitigation 2: Profiling + Health Data requires heavy safeguards to mitigate
    r_mit_2 = Imp()
    r_mit_2.set_as_rule("InitialHighRisk(?a), hasRiskTrigger(?a, ?t), ProfilingFeature(?t), hasSafeguard(?a, ?s1), HumanOversight(?s1), hasSafeguard(?a, ?s2), DataMinimization(?s2) -> MitigatedRiskSystem(?a)")
    
    # Mitigation 3: General High Risk mitigation (Hiring, Credit, Education) needs Human Oversight + Transparency
    r_mit_3 = Imp()
    r_mit_3.set_as_rule("InitialHighRisk(?a), hasSafeguard(?a, ?s1), HumanOversight(?s1), hasSafeguard(?a, ?s2), TransparencyMeasure(?s2) -> MitigatedRiskSystem(?a)")

def run_contextual_inference(triggers: list[str], safeguards: list[str], data_types: list[str] = None) -> dict:
    if data_types is None:
        data_types = []
        
    logger.info(f"Running Two-Stage SWRL reasoning. Triggers: {triggers}, Safeguards: {safeguards}")
    
    with onto:
        instance_id = f"system_{uuid.uuid4().hex[:8]}"
        sys_inst = AISystem(instance_id)
        
        applied_triggers = []
        applied_safeguards = []
        
        # 1. Map Triggers
        trigger_map = {
            "biometric": BiometricFeature,
            "emotion": EmotionRecognitionFeature,
            "profiling": ProfilingFeature,
            "automated decision": AutomatedDecisionFeature,
            "surveillance": SurveillanceFeature,
            "hiring": HiringFeature,
            "credit": CreditScoringFeature,
            "education": EducationalAssessmentFeature,
            "health": HealthcareFeature,
            "medical": HealthcareFeature
        }
        for t in triggers:
            t_low = t.lower()
            for key, cls in trigger_map.items():
                if key in t_low:
                    inst = cls()
                    sys_inst.hasRiskTrigger.append(inst)
                    applied_triggers.append(cls.__name__)
                    break
                    
        # 2. Map Safeguards
        safeguard_map = {
            "legal_basis": LegalBasis,
            "explicit_consent": ExplicitConsent,
            "human_oversight": HumanOversight,
            "data_minimization": DataMinimization,
            "anonymization": Anonymization,
            "pseudonymization": Pseudonymization,
            "purpose_limitation": PurposeLimitation,
            "security_measures": SecurityMeasure,
            "transparency_measures": TransparencyMeasure,
            "explainability_measures": ExplainabilityMeasure,
            "compliance_procedure": ComplianceProcedure
        }
        for s in safeguards:
            s_low = s.lower().replace(" ", "_")
            for key, cls in safeguard_map.items():
                if key in s_low:
                    inst = cls()
                    sys_inst.hasSafeguard.append(inst)
                    applied_safeguards.append(cls.__name__)
                    break
                    
        # 3. Process Data Types
        if "health" in " ".join(data_types).lower() or "medical" in " ".join(data_types).lower():
            sys_inst.processesData.append(SensitiveHealthData())
            
        try:
            # Run the HermiT Reasoner
            sync_reasoner_hermit(infer_property_values=True)
            
            # Extract Inferred Classes
            inferred_classes = [cls.name for cls in sys_inst.INDIRECT_is_a if hasattr(cls, 'name')]
            
            # Determine Initial Risk
            initial_risk = "MinimalRisk"
            if "InitialProhibitedRisk" in inferred_classes:
                initial_risk = "ProhibitedRisk"
            elif "InitialHighRisk" in inferred_classes:
                initial_risk = "HighRisk"
                
            # Determine Final Risk based on Mitigation
            final_risk = initial_risk
            is_mitigated = "MitigatedRiskSystem" in inferred_classes
            
            if is_mitigated:
                if initial_risk == "ProhibitedRisk":
                    final_risk = "HighRisk" # Mitigated down
                elif initial_risk == "HighRisk":
                    final_risk = "LimitedRisk" # Mitigated down
                    
            # Generate Explainability Trace
            trace = []
            if initial_risk == "MinimalRisk":
                trace.append("No critical risk triggers detected. Initial risk is MinimalRisk.")
            else:
                trace.append(f"Initial risk was classified as {initial_risk} due to triggers: {applied_triggers}.")
                
            if is_mitigated:
                trace.append(f"Final risk was reduced to {final_risk} because sufficient safeguards were detected: {applied_safeguards}.")
            else:
                if initial_risk != "MinimalRisk":
                    if applied_safeguards:
                        trace.append(f"Safeguards detected ({applied_safeguards}), but they were insufficient to mitigate the risk. Final risk remains {final_risk}.")
                    else:
                        trace.append(f"Final risk remains {final_risk} because no sufficient safeguards were detected.")

            # Calculate Composite Risk Score (10-100)
            base_scores = {
                "MinimalRisk": 100,
                "LimitedRisk": 75,
                "HighRisk": 50,
                "ProhibitedRisk": 25
            }
            composite_score = base_scores.get(final_risk, 50)
            
            # Weighted Penalties for triggers
            prohibited_triggers = {"EmotionRecognitionFeature", "BiometricFeature", "SurveillanceFeature"}
            for t in applied_triggers:
                if t in prohibited_triggers:
                    composite_score -= 10
                else:
                    composite_score -= 5
                
            # Bonuses for safeguards
            strong_safeguards = {"HumanOversight", "ExplicitConsent", "Anonymization", "LegalBasis"}
            for s in applied_safeguards:
                if s in strong_safeguards:
                    composite_score += 10
                else:
                    composite_score += 5
                    
            # Clamp the score between 0 and 100 (Natural floor)
            composite_score = max(0, min(100, composite_score))

            # Clean up instances
            for prop in list(sys_inst.hasRiskTrigger) + list(sys_inst.hasSafeguard) + list(sys_inst.processesData):
                destroy_entity(prop)
            destroy_entity(sys_inst)
            
            return {
                "initial_risk_level": initial_risk,
                "final_risk_level": final_risk,
                "composite_score": composite_score,
                "detected_risk_triggers": applied_triggers,
                "detected_safeguards": applied_safeguards,
                "missing_safeguards": [cls.__name__ for key, cls in safeguard_map.items() if cls.__name__ not in applied_safeguards],
                "reasoning_trace": trace
            }
            
        except Exception as e:
            logger.error(f"Reasoner error: {e}")
            return {
                "initial_risk_level": "Unknown",
                "final_risk_level": "Unknown",
                "composite_score": 10,
                "detected_risk_triggers": applied_triggers,
                "detected_safeguards": applied_safeguards,
                "missing_safeguards": [],
                "reasoning_trace": [f"Error during reasoning: {e}"]
            }


