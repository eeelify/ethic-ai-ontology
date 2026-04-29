from fastapi import FastAPI
from pydantic import BaseModel
from services.risk_analysis import analyze_text
from db.neo4j_client import close_driver

app = FastAPI()

class RequestModel(BaseModel):
    text: str

@app.get("/")
def root():
    return {"message": "API çalışıyor 🚀"}

@app.post("/analyze")
def analyze(req: RequestModel):
    result = analyze_text(req.text)

    return {
        "input_text": req.text,
        "analysis_result": result
    }

@app.on_event("shutdown")
def shutdown_db_client():
    close_driver()

#cd ai-ethics-backend
#venv\Scripts\activate
#uvicorn main:app --reload
#http://127.0.0.1:8000/docs