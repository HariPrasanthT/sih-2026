import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))
"""
Script 05: Build feature pipeline and generate training master dataset.
"""
import logging
# pyrefly: ignore [missing-import]
from src.features.feature_pipeline import generate_development_dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if __name__ == "__main__":
    logging.info("STEP 5: Executing Feature Engineering Pipeline...")
    df_master = generate_development_dataset()
    logging.info(f"Training master dataset generated with {len(df_master)} rows and {len(df_master.columns)} columns.")
