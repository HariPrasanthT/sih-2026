import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))
"""
Script 02: Ingest configured KaggleHub datasets.
"""
import logging
# pyrefly: ignore [missing-import]
from src.data.kaggle_ingestion import ingest_all_configured_kaggle_datasets

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if __name__ == "__main__":
    logging.info("STEP 2: Starting KaggleHub Ingestion...")
    downloaded = ingest_all_configured_kaggle_datasets()
    logging.info(f"Kaggle ingestion finished. Ingested {len(downloaded)} datasets.")
