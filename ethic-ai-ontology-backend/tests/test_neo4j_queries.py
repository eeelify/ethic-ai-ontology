import pytest
from db.profile import get_full_profile
from db.regulations import get_regulations_for_system
from db.violations import get_violations_for_system


def test_get_regulations_for_system(mocker):
    mocker.patch("db.regulations.run_query", return_value=[{"regulation": "GDPR"}])
    result = get_regulations_for_system("TestSystem")
    assert len(result) == 1
    assert result[0]["regulation"] == "GDPR"

def test_get_regulations_for_system_empty(mocker):
    mocker.patch("db.regulations.run_query", return_value=None)
    result = get_regulations_for_system("TestSystem")
    assert result is None

def test_get_violations(mocker):
    mocker.patch("db.violations.run_query", return_value=[{"violated_principle": "Fairness"}])
    result = get_violations_for_system("TestSystem")
    assert len(result) == 1
    assert result[0]["violated_principle"] == "Fairness"

from db.tensions import get_tensions_for_system, get_all_principle_conflicts

def test_get_tensions(mocker):
    mocker.patch("db.tensions.run_query", return_value=[{"tension": "Privacy vs Utility"}])
    result = get_tensions_for_system("TestSystem")
    assert len(result) == 1

def test_get_full_profile(mocker):
    mocker.patch("db.profile.run_query", return_value=[{"system": "SysA", "risk_level": "High"}])
    result = get_full_profile("SysA")
    assert result["system"] == "SysA"
    assert result["risk_level"] == "High"
