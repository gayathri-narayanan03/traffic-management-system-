"""
AI-Powered Traffic Management System — backend entry point.

Run with:  uvicorn main:app --reload
Docs at:   http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes import traffic, dashboard, history, incidents

app = FastAPI(
    title="AI-Powered Traffic Management System",
    description="Camera-based traffic monitoring, congestion analysis, and "
                "signal-timing recommendation API for a simulated four-way intersection.",
    version="1.0.0",
)

# Allow a locally-run frontend dashboard to call this API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {
        "message": "AI-Powered Traffic Management System API",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(traffic.router)
app.include_router(dashboard.router)
app.include_router(history.router)
app.include_router(incidents.router)
