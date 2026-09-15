"""
FastAPI Application Entrypoint for SIH 26006.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# pyrefly: ignore [missing-import]
from src.api.routes import router

app = FastAPI(
    title="AI-Driven Indian East Coast Freight Forecasting & Vessel Charter Recommendation System",
    description="Backend API for SAIL / Ministry of Steel Bulk Procurement and Vessel Charter Optimization (SIH 26006)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://vercel.app",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|.*\.vercel\.app)(:[0-9]+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "project": "SIH 26006",
        "title": "AI Freight Forecasting & Vessel Charter Recommendation Backend",
        "status": "OPERATIONAL",
        "docs": "/docs"
    }
