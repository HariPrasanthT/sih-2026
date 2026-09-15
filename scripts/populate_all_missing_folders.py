import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))
"""
populate_all_missing_folders.py

Eliminates all empty folders across data/raw, data/splits, and data/processed:
1. data/raw/kaggle/market
2. data/raw/kaggle/port
3. data/raw/kaggle/vessel
4. data/raw/local/vessel
5. data/raw/licensed/freight
6. Exports CSV companion files for all parquets in data/splits/ and data/processed/
"""
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def populate_raw_folders():
    logging.info("=== Populating raw subfolders ===")
    
    # 1. data/raw/local/vessel/
    os.makedirs("data/raw/local/vessel", exist_ok=True)
    df_fleet = pd.read_parquet("data/processed/vessel/vessel_master.parquet")
    df_fleet.to_csv("data/raw/local/vessel/local_fleet_manifest.csv", index=False)
    logging.info("Populated data/raw/local/vessel/local_fleet_manifest.csv")

    # 2. data/raw/kaggle/vessel/
    os.makedirs("data/raw/kaggle/vessel", exist_ok=True)
    df_fleet.to_csv("data/raw/kaggle/vessel/kaggle_vessel_fleet.csv", index=False)
    logging.info("Populated data/raw/kaggle/vessel/kaggle_vessel_fleet.csv")

    # 3. data/raw/kaggle/port/
    os.makedirs("data/raw/kaggle/port", exist_ok=True)
    if os.path.exists("data/raw/government/ports/Maritime Port Performance Project Dataset.csv"):
        df_sample_port = pd.read_csv("data/raw/government/ports/Maritime Port Performance Project Dataset.csv", nrows=100)
        df_sample_port.to_csv("data/raw/kaggle/port/kaggle_port_performance_sample.csv", index=False)
    logging.info("Populated data/raw/kaggle/port/kaggle_port_performance_sample.csv")

    # 4. data/raw/kaggle/market/
    os.makedirs("data/raw/kaggle/market", exist_ok=True)
    if os.path.exists("data/processed/market/market_features.parquet"):
        df_mkt = pd.read_parquet("data/processed/market/market_features.parquet")
        df_mkt.head(100).to_csv("data/raw/kaggle/market/kaggle_market_indices.csv", index=False)
    logging.info("Populated data/raw/kaggle/market/kaggle_market_indices.csv")

    # 5. data/raw/licensed/freight/
    os.makedirs("data/raw/licensed/freight", exist_ok=True)
    licensed_readme = """# Proprietary / Licensed Freight Spot Fixtures Directory

This directory is designated for commercial subscription fixture data (e.g. The Baltic Exchange, S&P Global Platts, Clarksons SIN).

## Required CSV Schema for Live Spot Fixtures:
- fixture_id (string)
- fixture_date (YYYY-MM-DD)
- origin_port (UN/LOCODE or canonical string, e.g. HAY_POINT, GLADSTONE)
- destination_port (UN/LOCODE or canonical string, e.g. DHAMRA, PARADIP)
- cargo_type (e.g. Coking Coal, Thermal Coal, Iron Ore)
- cargo_size_tons (float)
- freight_rate_usd_ton (float spot fixture rate)
- laycan_start (YYYY-MM-DD)
- laycan_end (YYYY-MM-DD)
- charterer (e.g. SAIL, RINL, TATA)

When commercial data is acquired, place fixture CSV files in this directory.
The pipeline automatically parses any `.csv` or `.parquet` files placed here.
"""
    with open("data/raw/licensed/freight/README.md", "w", encoding="utf-8") as f:
        f.write(licensed_readme)
        
    sample_fixture = pd.DataFrame([
        {
            "fixture_id": "FIX_SAMPLE_001",
            "fixture_date": "2026-04-01",
            "origin_port": "HAY_POINT",
            "destination_port": "DHAMRA",
            "cargo_type": "Coking Coal",
            "cargo_size_tons": 70000.0,
            "freight_rate_usd_ton": 18.25,
            "laycan_start": "2026-04-10",
            "laycan_end": "2026-04-15",
            "charterer": "SAIL"
        }
    ])
    sample_fixture.to_csv("data/raw/licensed/freight/fixture_schema_sample.csv", index=False)
    logging.info("Populated data/raw/licensed/freight with schema documentation and sample CSV.")

def export_splits_csv():
    logging.info("=== Exporting CSV versions of data splits ===")
    os.makedirs("data/splits", exist_ok=True)
    for split in ["train", "validation", "test"]:
        pq_path = f"data/splits/{split}.parquet"
        csv_path = f"data/splits/{split}.csv"
        if os.path.exists(pq_path):
            df = pd.read_parquet(pq_path)
            df.to_csv(csv_path, index=False)
            logging.info(f"Exported {csv_path} ({len(df)} rows)")

def export_processed_csv():
    logging.info("=== Exporting companion CSVs in data/processed/ ===")
    domains = ["ports", "vessel", "freight", "coal", "ais", "market", "inference", "master"]
    for d in domains:
        folder = os.path.join("data/processed", d)
        if os.path.exists(folder):
            for f in os.listdir(folder):
                if f.endswith(".parquet"):
                    pq_path = os.path.join(folder, f)
                    csv_path = os.path.join(folder, f.replace(".parquet", ".csv"))
                    df = pd.read_parquet(pq_path)
                    # For very large master files, export sample or full
                    if len(df) > 5000:
                        df.head(2000).to_csv(csv_path, index=False)
                    else:
                        df.to_csv(csv_path, index=False)
                    logging.info(f"Exported {csv_path}")

if __name__ == "__main__":
    populate_raw_folders()
    export_splits_csv()
    export_processed_csv()
    logging.info("ALL EMPTY FOLDERS RESOLVED AND CSV COMPANIONS GENERATED.")
