import pytest

def test_violations_endpoint_valid(client, mocker):
    mocker.patch("routers.violations.individual_exists", return_value=True)
    mocker.patch("routers.violations.get_violations_for_system", return_value=[
        {"violated_principle": "Fairness", "explanation": "Biased dataset"}
    ])
    
    response = client.get("/violations/TestSystem")
    assert response.status_code == 200
    data = response.json()
    assert data["system"] == "TestSystem"
    assert "violated_principles" in data
    assert data["violation_count"] == 1
    assert "Fairness" in data["violated_principles"]

def test_violations_endpoint_empty(client, mocker):
    mocker.patch("routers.violations.individual_exists", return_value=True)
    mocker.patch("routers.violations.get_violations_for_system", return_value=[])
    
    response = client.get("/violations/SafeSystem")
    assert response.status_code == 200
    data = response.json()
    assert data["system"] == "SafeSystem"
    assert data["violation_count"] == 0
    assert len(data["violated_principles"]) == 0

def test_violations_endpoint_missing_system(client):
    response = client.get("/violations")
    assert response.status_code == 404
