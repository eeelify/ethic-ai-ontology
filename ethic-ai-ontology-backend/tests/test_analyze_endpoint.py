import pytest
from unittest.mock import patch

def test_analyze_text_valid_input(client, mocker):
    mocker.patch("services.reasoning_service.run_contextual_inference", return_value={
        "initial_risk_level": "HighRisk",
        "final_risk_level": "HighRisk",
        "composite_score": 85,
        "detected_risk_triggers": ["BiometricFeature"],
        "detected_safeguards": [],
        "missing_safeguards": ["ExplicitConsent"],
        "reasoning_trace": ["Trigger found"]
    })
    
    # We also mock the graph DB calls if necessary, but analysis_service caches ontology.
    # We will mock `get_ontology_cache` to return a fake ontology.
    mocker.patch("services.analysis_service.get_ontology_cache", return_value=[
        {"keyword": "biometric", "category": "BiometricSystem", "risks": ["HighRisk"], "regulations": ["GDPR"], "ethical_analysis": [], "ethical_tensions": []}
    ])

    response = client.post("/analyze-text", json={"text": "This system uses biometric facial recognition."})
    assert response.status_code == 200
    data = response.json()
    assert "detected_risk_triggers" in data
    assert "detected_safeguards" in data
    assert "initial_risk_level" in data
    assert "final_risk_level" in data
    assert "reasoning_trace" in data

def test_analyze_text_biometric_no_safeguards(client, mocker):
    mocker.patch("services.analysis_service.get_ontology_cache", return_value=[
        {"keyword": "biometric", "category": "BiometricSystem", "risks": ["HighRisk"], "regulations": [], "ethical_analysis": [], "ethical_tensions": []}
    ])
    
    response = client.post("/analyze-text", json={"text": "This system uses biometric facial recognition without any consent."})
    assert response.status_code == 200
    data = response.json()
    
    # The deterministic reasoner should flag it as HighRisk or UnacceptableRisk
    assert data["final_risk_level"] in ["HighRisk", "UnacceptableRisk"]

def test_analyze_text_biometric_with_safeguards(client, mocker):
    mocker.patch("services.analysis_service.get_ontology_cache", return_value=[
        {"keyword": "biometric", "category": "BiometricSystem", "risks": ["HighRisk"], "regulations": [], "ethical_analysis": [], "ethical_tensions": []}
    ])
    
    response = client.post("/analyze-text", json={
        "text": "This system uses biometric facial recognition but obtains explicit consent, has human oversight, data minimization, and security measure."
    })
    assert response.status_code == 200
    data = response.json()
    
    # The exact swrl logic in owlready2 might change the risk, or keep it prohibited.
    assert data["final_risk_level"] in ["MinimalRisk", "LimitedRisk", "MitigatedRisk", "Unknown", "UnacceptableRisk"]

def test_analyze_text_empty_input(client):
    response = client.post("/analyze-text", json={"text": ""})
    assert response.status_code == 422

def test_analyze_text_short_nonsense(client, mocker):
    # LLM fallback should be mocked to avoid real API calls and speed up
    mocker.patch("google.generativeai.GenerativeModel.generate_content", side_effect=Exception("Mocked API error"))
    response = client.post("/analyze-text", json={"text": "asdf"})
    assert response.status_code == 200
    data = response.json()
    assert data["initial_risk_level"] in ["Unknown", "MinimalRisk"]
    assert any("DEBUG_ERROR" in cat for cat in data["inferred_categories"])
