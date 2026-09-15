import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))
import logging
# pyrefly: ignore [missing-import]
from src.data.discovery import discover_all_datasets

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if __name__ == "__main__":
    logging.info("STEP 1: Starting Dataset Discovery...")
    report = discover_all_datasets()
    logging.info(f"Discovery complete. Found {report['discovered_files_count']} files.")
