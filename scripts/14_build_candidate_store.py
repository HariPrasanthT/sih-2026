import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))
"""
Script 14: Build candidate fleet master and port constraint store.
"""
import logging
# pyrefly: ignore [missing-import]
from src.data.port_mapping import export_port_master_tables
# pyrefly: ignore [missing-import]
from src.data.vessel_mapping import export_vessel_master_table

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if __name__ == "__main__":
    logging.info("STEP 14: Exporting Candidate Store and Port Constraints...")
    export_port_master_tables()
    export_vessel_master_table()
    logging.info("Candidate store ready.")
