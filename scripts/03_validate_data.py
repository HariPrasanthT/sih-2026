import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))
import logging
# pyrefly: ignore [missing-import]
from src.data.local_ingestion import ingest_all_local_datasets
# pyrefly: ignore [missing-import]
from src.data.government_ingestion import process_all_government_data
# pyrefly: ignore [missing-import]
from src.data.quality import generate_data_quality_report
# pyrefly: ignore [missing-import]
from src.data.loaders import load_port_master, load_vessel_master, load_port_congestion

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if __name__ == "__main__":
    logging.info("STEP 3: Validating Data and Generating Quality Reports...")
    ingest_all_local_datasets()
    process_all_government_data()
    
    ports_df = load_port_master()
    vessels_df = load_vessel_master()
    cong_df = load_port_congestion()
    
    datasets = {
        "port_master": ports_df,
        "vessel_master": vessels_df
    }
    if cong_df is not None:
        datasets["port_congestion_daily"] = cong_df
        
    generate_data_quality_report(datasets)
    logging.info("Data validation and quality report complete.")
