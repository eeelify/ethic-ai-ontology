import pytest

def test_tensions_endpoint_valid(client, mocker):
    mocker.patch("routers.tensions.individual_exists", return_value=True)
    mocker.patch("routers.tensions.get_tensions_for_system", return_value=[{"tension": "Privacy vs Transparency"}])
    mocker.patch("routers.tensions.get_all_principle_conflicts", return_value=[{"principle_1": "Privacy", "principle_2": "Transparency"}])
    
    response = client.get("/tensions/TestSystem")
    assert response.status_code == 200
    data = response.json()
    assert data["system"] == "TestSystem"
    assert "ethical_tensions" in data
    assert "Privacy vs Transparency" in data["ethical_tensions"]
    assert len(data["principle_conflicts"]) == 1

def test_tensions_endpoint_empty(client, mocker):
    mocker.patch("routers.tensions.individual_exists", return_value=True)
    mocker.patch("routers.tensions.get_tensions_for_system", return_value=[])
    mocker.patch("routers.tensions.get_all_principle_conflicts", return_value=[])
    
    response = client.get("/tensions/SafeSystem")
    assert response.status_code == 200
    data = response.json()
    assert len(data["ethical_tensions"]) == 0
    assert len(data["principle_conflicts"]) == 0

def test_tensions_endpoint_missing_system(client):
    response = client.get("/tensions")
    assert response.status_code == 404
