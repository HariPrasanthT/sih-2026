"""
Root entrypoint for Uvicorn: uvicorn api:app --reload
"""
# pyrefly: ignore [missing-import]
from src.api.app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
