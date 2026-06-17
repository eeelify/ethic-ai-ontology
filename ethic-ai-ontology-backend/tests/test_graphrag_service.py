import pytest
from services.graphrag import run_graphrag_pipeline, NoGeminiModelAvailable

def test_run_graphrag_pipeline(mocker):
    # Mock Neo4j profile
    mocker.patch("services.graphrag.get_dynamic_profile", return_value={"system": "TestSystem", "relationships": {}})
    
    # Mock analysis_service
    mocker.patch("services.graphrag.analyze_text", return_value={
        "inferred_categories": ["AI System"],
        "inferred_regulations": ["GDPR"],
        "final_risk_level": "HighRisk",
        "composite_score": 85
    })
    
    # Mock chromadb retrieval
    mocker.patch("services.graphrag.retrieve_legal_context", return_value=[
        {"text": "GDPR text", "source": "EU", "article": "Art 5", "category": "Data"}
    ])
    
    # Mock Gemini generation
    mocker.patch("services.graphrag._generate_report_with_model_fallback", return_value=({
        "executive_summary": "Test summary",
        "risk_assessment": "High risk",
        "composite_risk_score": 85,
        "risk_level": "HighRisk",
        "ethical_analysis": "Ethical analysis here",
        "ethical_tensions": [],
        "regulations": ["GDPR"]
    }, "mock-model"))

    result = run_graphrag_pipeline("TestSystem", "Test text")
    assert result["system"] == "TestSystem"
    assert "report" in result
    assert result["report"]["risk_level"] == "HighRisk"
    assert len(result["legal_sources_used"]) == 1

def test_graphrag_fallback_on_gemini_failure(mocker):
    mocker.patch("services.graphrag.get_dynamic_profile", return_value={})
    mocker.patch("services.graphrag.analyze_text", return_value={})
    mocker.patch("services.graphrag.retrieve_legal_context", return_value=[])
    
    mocker.patch("services.graphrag._generate_report_with_model_fallback", side_effect=NoGeminiModelAvailable([], None))
    
    with pytest.raises(NoGeminiModelAvailable):
        run_graphrag_pipeline("TestSystem", "Test")
