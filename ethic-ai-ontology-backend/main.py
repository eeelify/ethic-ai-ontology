from dotenv import load_dotenv

# Windows’ta kullanıcı/sistem ortamında eski veya boş GEMINI_* varsa .env’deki değer
# varsayılan load_dotenv ile yüklenmez; override=True .env’i önceliklendirir.
load_dotenv(override=True)

from fastapi import FastAPI

from db.connection import close_driver
from routers import (
    analyze_router,
    assess_router,
    query_router,
    report_router,
    risk_router,
    systems_router,
    tensions_router,
    violations_router,
)

app = FastAPI(title="Ethic AI Ontology Backend")


@app.get("/")
def root():
    return {"status": "ok"}


app.include_router(systems_router, prefix="/systems", tags=["systems"])
app.include_router(risk_router, prefix="/risk", tags=["risk"])
app.include_router(query_router, prefix="/query", tags=["query"])
app.include_router(analyze_router, tags=["analyze"])
app.include_router(violations_router, prefix="/violations", tags=["violations"])
app.include_router(tensions_router, prefix="/tensions", tags=["tensions"])
app.include_router(assess_router, prefix="/assess", tags=["assess"])
app.include_router(report_router, tags=["report"])


@app.on_event("shutdown")
def shutdown_db_client():
    close_driver()


#.\venv\Scripts\Activate.ps1
#uvicorn main:app --reload
#http://127.0.0.1:8000/docs .

