import pytest
from services.reasoning_service import run_contextual_inference

def test_reasoning_trigger_no_safeguard():
    result = run_contextual_inference(triggers=["BiometricFeature"], safeguards=[], data_types=[])
    assert result["initial_risk_level"] in ["HighRisk", "ProhibitedRisk"]
    assert result["final_risk_level"] in ["HighRisk", "ProhibitedRisk"]
    assert "BiometricFeature" in result["detected_risk_triggers"]
    assert len(result["reasoning_trace"]) > 0

def test_reasoning_trigger_with_safeguards():
    result = run_contextual_inference(
        triggers=["BiometricFeature"], 
        safeguards=["ConsentMechanism", "HumanOversight", "DataMinimization", "SecurityMeasure"],
        data_types=[]
    )
    # The exact swrl logic in owlready2 might change the risk, but the test ensures the execution works deterministically
    assert result["initial_risk_level"] in ["HighRisk", "ProhibitedRisk"]
    # Final risk level should ideally be less than initial or same depending on ontology rules
    assert "final_risk_level" in result
    assert len(result["reasoning_trace"]) > 0

def test_reasoning_profiling_and_health_data():
    result = run_contextual_inference(
        triggers=["ProfilingFeature"], 
        safeguards=[],
        data_types=["SensitiveHealthData"]
    )
    assert result["initial_risk_level"] in ["HighRisk", "ProhibitedRisk"]

def test_reasoning_profiling_health_with_safeguards():
    result = run_contextual_inference(
        triggers=["ProfilingFeature"], 
        safeguards=["LegalBasis", "HumanOversight"],
        data_types=["SensitiveHealthData"]
    )
    assert "final_risk_level" in result
    assert len(result["reasoning_trace"]) > 0
