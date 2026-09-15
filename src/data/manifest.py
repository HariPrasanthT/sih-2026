"""
Data Manifest and Lineage Registry.
Tracks SHA256 hashes, provenance, geographic scope, date ranges, and intended use.
"""
import os
import json
import hashlib
import logging
from typing import Dict, Any, List, Optional
import pandas as pd

logger = logging.getLogger(__name__)

MANIFEST_PATH = "data/metadata/data_manifest.json"


def compute_sha256(file_path: str, chunk_size: int = 65536) -> str:
    """Compute SHA256 checksum for a file."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        logger.error(f"Failed to compute SHA256 for {file_path}: {e}")
        return ""


def load_manifest(manifest_path: str = MANIFEST_PATH) -> Dict[str, Any]:
    """Load existing manifest or initialize new one."""
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"version": "1.0.0", "updated_at": "", "datasets": {}}


def register_dataset(
    dataset_name: str,
    local_path: str,
    source_type: str, # "LOCAL_FILE", "KAGGLE", "GOVERNMENT", "SYNTHETIC"
    scope: str, # "INDIA_REAL", "GLOBAL_SUPPORTING", "SYNTHETIC_DEVELOPMENT_ONLY"
    intended_use: str,
    source_url: str = "",
    date_range: str = "Unknown",
    license_info: str = "Internal / Research / Open",
    rows: int = 0,
    columns: Optional[List[str]] = None,
    limitations: str = "",
    manifest_path: str = MANIFEST_PATH
) -> None:
    """Register or update an entry in data_manifest.json."""
    manifest = load_manifest(manifest_path)
    file_hash = compute_sha256(local_path) if os.path.exists(local_path) else ""
    
    entry = {
        "dataset_name": dataset_name,
        "local_path": local_path.replace("\\", "/"),
        "source_type": source_type,
        "source_url": source_url,
        "geographic_scope": scope,
        "sha256_hash": file_hash,
        "ingestion_timestamp": pd.Timestamp.now(tz="UTC").isoformat(),
        "date_range": date_range,
        "license": license_info,
        "row_count": rows,
        "columns": columns or [],
        "intended_use": intended_use,
        "limitations": limitations
    }
    
    manifest["datasets"][dataset_name] = entry
    manifest["updated_at"] = pd.Timestamp.now(tz="UTC").isoformat()
    
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
        
    logger.info(f"Registered dataset '{dataset_name}' ({scope}) in manifest.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Manifest manager initialized.")
