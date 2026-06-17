import pytest

def test_report_endpoint_valid(client, mocker):
    mocker.patch("db.systems.get_system_saved_report", return_value=None)
    mocker.patch("routers.report.run_graphrag_pipeline", return_value={
        "system": "TestSystem",
        "dynamic_profile": {},
        "inferred_data": {},
        "legal_sources_used": ["GDPR Art 5"],
        "report": {
            "risk_assessment": "High risk due to...",
            "ethical_violations": [],
            "ethical_tensions": [],
            "regulations": ["GDPR"],
            "ontology_evidence_used": True,
            "recommendations": ["Do this"]
        },
        "gemini_model": "mock-model"
    })
    
    response = client.post("/report", json={"system_name": "TestSystem", "text": "Something"})
    assert response.status_code == 200
    data = response.json()
    assert data["system"] == "TestSystem"
    assert "report" in data
    assert "risk_assessment" in data["report"]
    assert "ethical_tensions" in data["report"]

def test_report_endpoint_gemini_error(client, mocker):
    from google.api_core import exceptions as google_api_exceptions
    mocker.patch("db.systems.get_system_saved_report", return_value=None)
    mocker.patch("routers.report.run_graphrag_pipeline", side_effect=google_api_exceptions.GoogleAPIError("API limit exceeded"))
    
    response = client.post("/report", json={"system_name": "TestSystem"})
    # It should catch the error and return 502
    assert response.status_code == 502
    assert "Gemini API hatas" in response.json()["detail"]

def test_report_endpoint_missing_input(client):
    response = client.post("/report", json={})
    assert response.status_code == 422
