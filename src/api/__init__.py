"""
FastAPI REST API Layer for Indian East Coast Freight Forecasting & Vessel Chartering.
"""
# pyrefly: ignore [missing-import]
from src.api.app import app
# pyrefly: ignore [missing-import]
from src.api.routes import router

__all__ = ["app", "router"]
