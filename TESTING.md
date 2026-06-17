# Testing Guide

This project contains a comprehensive test suite covering the ontology reasoning logic, FastAPI backend endpoints, GraphRAG pipeline, Neo4j queries, frontend components, and performance.

## 1. Backend Tests (Pytest)

The backend tests are located in `ethic-ai-ontology-backend/tests`. They mock external dependencies (Neo4j, Google Gemini, ChromaDB) to run deterministically.

### Running Backend Tests
Navigate to the backend directory:
```bash
cd ethic-ai-ontology-backend
python -m pytest tests -v
```

### Running with Coverage
To generate an HTML coverage report:
```bash
python -m pytest tests --cov=. --cov-report=html
```

## 2. Frontend Tests (Vitest & React Testing Library)

The frontend tests are located in `ethic-ai-ontology-frontend/src/tests`. They verify component rendering and user interaction.

### Running Frontend Tests
Navigate to the frontend directory:
```bash
cd ethic-ai-ontology-frontend
npm run test
```

## 3. Performance Tests (Locust)

Performance tests simulate concurrent users hitting the assessment, violations, tensions, and report endpoints. The LLM-heavy `/report` endpoint is assigned a lower request weight.

### Running Performance Tests
Start the backend server first:
```bash
cd ethic-ai-ontology-backend
python -m uvicorn main:app --reload
```

Navigate to the backend directory in another terminal:
```bash
cd ethic-ai-ontology-backend
locust -f performance/locustfile.py --host http://127.0.0.1:8000
```
Then open `http://localhost:8089` to start the swarm.

### Checking API Status
You can verify the backend is running using the health endpoint:
```bash
curl http://127.0.0.1:8000/health
```
Or view the Swagger documentation at `http://127.0.0.1:8000/docs`.

---

## Test Summary

| Test Category | Tested Component | Expected Result | Status |
|---------------|------------------|-----------------|--------|
| Ontology Reasoning Tests | `run_contextual_inference` | Returns initial and final risk deterministically based on triggers and safeguards | ✅ Implemented |
| API Endpoint Tests | `/analyze-text`, `/violations`, `/tensions` | Valid responses, correct status codes, robust error handling | ✅ Implemented |
| API Endpoint Tests | `/report` | Generates report using mocked LLM, gracefully handles Gemini API failures | ✅ Implemented |
| Neo4j Query Tests | `get_violations`, `get_regulations`, etc. | Queries return proper lists or empty lists without crashing | ✅ Implemented |
| GraphRAG Tests | `run_graphrag_pipeline` | Merges contexts and generates a valid report dict; throws `NoGeminiModelAvailable` on fallback failure | ✅ Implemented |
| Frontend Tests | `AnalyzerPage` Component | Input changes reflect, Analyze button triggers mocked API, results display correctly | ✅ Implemented |
| Performance Tests | Multiple Endpoints | Endpoints withstand concurrent loads using weighted Locust tasks | ✅ Implemented |
| Error Handling Tests | API Endpoints | Missing data yields 422, backend does not crash on empty results | ✅ Implemented |
