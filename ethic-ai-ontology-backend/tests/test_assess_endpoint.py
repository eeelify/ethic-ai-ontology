import pytest

def test_assess_valid_input(client, mocker):
    mocker.patch("routers.assess.get_full_profile", return_value={
        "system": "TestSystem",
        "risk_level": "HighRisk",
        "sector": "HR",
        "violated_principles": ["Fairness"],
        "ethical_tensions": ["Privacy vs Utility"],
        "requirements": ["Consent"]
    })
    
    mocker.patch("routers.assess.get_session")

    response = client.post("/assess", json={
        "system_name": "TestSystem",
        "ethical_score": 80.0,
        "legal_score": 60.0,
        "data_score": 75.0,
        "technical_score": 50.0,
        "oversight_score": 40.0
    })

    assert response.status_code == 200
    data = response.json()
    assert "risk_level" in data
    assert "composite_risk_score" in data
    assert data["system"] == "TestSystem"
    assert data["sector"] == "HR"

def test_assess_missing_system_name(client):
    response = client.post("/assess", json={
        "system_name": "",
        "ethical_score": 80.0
    })
    assert response.status_code == 422
