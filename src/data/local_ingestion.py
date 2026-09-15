"""
Local Data Ingestion Engine.
Copies and indexes local files into interim stages without altering raw files.
"""
import os
import shutil
import logging
from typing import List, Dict, Any, Optional
import pandas as pd

# pyrefly: ignore [missing-import]
from src.data.manifest import register_dataset

logger = logging.getLogger(__name__)


def ingest_local_port_traffic(
    source_dir: str = "cargo traffic data",
    dest_dir: str = "data/raw/government/traffic"
) -> List[str]:
    """Ingest IPA / Indian Major Port traffic reports."""
    os.makedirs(dest_dir, exist_ok=True)
    copied = []
    if not os.path.exists(source_dir):
        logger.warning(f"Source directory {source_dir} not found.")
        return copied
        
    for file in os.listdir(source_dir):
        if file.lower().endswith(".csv") or file.lower().endswith(".xlsx"):
            src = os.path.join(source_dir, file)
            dst = os.path.join(dest_dir, file)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
            copied.append(dst)
            
            # Register in manifest
            register_dataset(
                dataset_name=f"local_traffic_{file}",
                local_path=dst,
                source_type="GOVERNMENT",
                scope="INDIA_REAL",
                intended_use="Port throughput and historical traffic handling features",
                limitations="Annual / monthly official port statistics from Indian Port Association (IPA)"
            )
    logger.info(f"Ingested {len(copied)} port traffic files to {dest_dir}")
    return copied


def ingest_local_commodity_prices(
    source_dir: str = "Commodity Coal Prices",
    dest_dir: str = "data/raw/local/coal"
) -> List[str]:
    """Ingest local coal / commodity benchmark prices."""
    os.makedirs(dest_dir, exist_ok=True)
    copied = []
    if not os.path.exists(source_dir):
        return copied
        
    for file in os.listdir(source_dir):
        if file.lower().endswith(".csv") or file.lower().endswith(".xlsx"):
            src = os.path.join(source_dir, file)
            dst = os.path.join(dest_dir, file)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
            copied.append(dst)
            
            register_dataset(
                dataset_name=f"local_coal_{file}",
                local_path=dst,
                source_type="LOCAL_FILE",
                scope="GLOBAL_SUPPORTING",
                intended_use="Global commodity benchmark pricing for fuel and cargo",
                limitations="Historical benchmark price indices"
            )
    return copied


def ingest_all_local_datasets() -> Dict[str, List[str]]:
    """Ingest all discovered local sources."""
    results = {
        "traffic": ingest_local_port_traffic(),
        "coal": ingest_local_commodity_prices()
    }
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ingest_all_local_datasets()
