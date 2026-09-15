"""
Indian Government and Port Operational Data Ingestion & Parser.
Extracts port calls, dry bulk traffic, cargo throughput, and derives Indian East Coast congestion time series.
"""
import os
import glob
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import requests

# pyrefly: ignore [missing-import]
from src.data.port_mapping import normalize_port_name, CANONICAL_PORTS
# pyrefly: ignore [missing-import]
from src.data.manifest import register_dataset

logger = logging.getLogger(__name__)


def process_daily_port_activity(
    raw_csv_path: str = "Global Daily Port Activity and Trade Estimates/Daily_Port_Activity_Data_and_Trade_Estimates.csv",
    output_parquet: str = "data/processed/ports/port_congestion.parquet"
) -> Optional[pd.DataFrame]:
    """
    Extract daily port calls, dry bulk calls, imports, and exports for Indian East Coast ports.
    Derives normalized daily port activity and waiting pressure.
    """
    if not os.path.exists(raw_csv_path):
        logger.warning(f"File not found: {raw_csv_path}")
        return None
        
    logger.info("Processing daily port activity dataset...")
    # Load IND rows
    chunks = []
    chunksize = 100000
    for chunk in pd.read_csv(raw_csv_path, chunksize=chunksize, low_memory=False):
        ind_chunk = chunk[chunk["ISO3"] == "IND"].copy()
        if not ind_chunk.empty:
            chunks.append(ind_chunk)
            
    if not chunks:
        logger.warning("No Indian port records found in daily dataset.")
        return None
        
    df_ind = pd.concat(chunks, ignore_index=True)
    logger.info(f"Loaded {len(df_ind)} Indian port daily records.")
    
    # Map port names to canonical East Coast names
    df_ind["canonical_port"] = df_ind["portname"].apply(normalize_port_name)
    
    # Filter to Indian East Coast canonical ports
    east_coast_ports = [p for p, data in CANONICAL_PORTS.items() if data.get("coast") == "East Coast"]
    df_ec = df_ind[df_ind["canonical_port"].isin(east_coast_ports)].copy()
    
    if df_ec.empty:
        logger.warning("No canonical East Coast records found after mapping.")
        return None
        
    # Standardize columns
    df_ec["date"] = pd.to_datetime(df_ec["date"].str[:10], errors="coerce")
    df_ec = df_ec.dropna(subset=["date"])
    df_ec["portcalls_dry_bulk"] = pd.to_numeric(df_ec.get("portcalls_dry_bulk", 0), errors="coerce").fillna(0)
    df_ec["portcalls_total"] = pd.to_numeric(df_ec.get("portcalls_total", df_ec.get("portcalls_container", 0) + df_ec["portcalls_dry_bulk"]), errors="coerce").fillna(0)
    df_ec["import_cargo_mt"] = pd.to_numeric(df_ec.get("import_cargo", 0), errors="coerce").fillna(0) / 1000.0  # normalize
    df_ec["export_cargo_mt"] = pd.to_numeric(df_ec.get("export_cargo", 0), errors="coerce").fillna(0) / 1000.0
    
    # Group by date and canonical port
    df_daily = df_ec.groupby(["date", "canonical_port"]).agg({
        "portcalls_dry_bulk": "sum",
        "portcalls_total": "sum",
        "import_cargo_mt": "sum",
        "export_cargo_mt": "sum"
    }).reset_index()
    
    # Derive rolling operational metrics & congestion index
    df_daily = df_daily.sort_values(["canonical_port", "date"]).reset_index(drop=True)
    
    # Rolling dry bulk pressure and estimated waiting time
    df_daily["dry_bulk_calls_7d_avg"] = df_daily.groupby("canonical_port")["portcalls_dry_bulk"].transform(lambda x: x.rolling(7, min_periods=1).mean())
    df_daily["dry_bulk_calls_30d_avg"] = df_daily.groupby("canonical_port")["portcalls_dry_bulk"].transform(lambda x: x.rolling(30, min_periods=1).mean())
    
    # Derived Congestion Index: based on dry bulk calls relative to 30d baseline + import surge
    def compute_congestion(group):
        mean_calls = group["dry_bulk_calls_30d_avg"].replace(0, 1.0)
        surge_ratio = group["dry_bulk_calls_7d_avg"] / mean_calls
        # Sigmoid-normalized congestion index [0, 1]
        c_idx = 1.0 / (1.0 + np.exp(-1.5 * (surge_ratio - 1.0)))
        return pd.Series(c_idx, index=group.index)
        
    df_daily["derived_congestion_index"] = df_daily.groupby("canonical_port", group_keys=False).apply(compute_congestion)
    # Estimated waiting days
    df_daily["est_waiting_days"] = np.clip(df_daily["derived_congestion_index"] * 4.5, 0.5, 6.0)
    
    os.makedirs(os.path.dirname(output_parquet), exist_ok=True)
    df_daily.to_parquet(output_parquet, index=False)
    
    register_dataset(
        dataset_name="processed_port_congestion",
        local_path=output_parquet,
        source_type="LOCAL_FILE",
        scope="INDIA_REAL",
        intended_use="India East Coast port daily activity, dry bulk traffic, and congestion index",
        rows=len(df_daily),
        columns=list(df_daily.columns),
        limitations="Derived from Global Daily Port Activity and Trade Estimates official reporting"
    )
    
    logger.info(f"Saved processed port congestion table ({len(df_daily)} rows) to {output_parquet}")
    return df_daily


def process_all_government_data() -> Dict[str, Any]:
    """Process all Indian government and port tables."""
    res = {}
    df_cong = process_daily_port_activity()
    if df_cong is not None:
        res["port_congestion_rows"] = len(df_cong)
    return res


def fetch_data_gov_in_resource(resource_id: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Query Open Government Data (OGD) Platform India (data.gov.in) API for a specific resource ID.
    Reads DATA_GOV_IN_API_KEY from environment or .env.
    """
    key = os.environ.get("DATA_GOV_IN_API_KEY", "").strip()
    if not key:
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("DATA_GOV_IN_API_KEY="):
                        key = line.split("=", 1)[1].strip()
                        break

    if not key:
        logger.warning("DATA_GOV_IN_API_KEY is not configured.")
        return []

    url = f"https://api.data.gov.in/resource/{resource_id}?api-key={key}&format=json&offset={offset}&limit={limit}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            records = data.get("records", [])
            logger.info(f"Retrieved {len(records)} records from data.gov.in resource '{resource_id}'.")
            return records
        else:
            logger.warning(f"data.gov.in request returned status {resp.status_code}: {resp.text[:150]}")
    except Exception as e:
        logger.warning(f"Failed to fetch data.gov.in resource '{resource_id}': {e}")

    return []


def ingest_live_indian_coal_dispatch(
    resource_id: str = "e6383191-0c60-4e11-ace3-5ddac243822b",
    output_csv: str = "data/raw/government/coal/monthly_coal_production_dispatch.csv",
    output_parquet: str = "data/processed/coal/monthly_coal_production_dispatch.parquet"
) -> Optional[pd.DataFrame]:
    """
    Ingest live Monthly Coal/Lignite Production and Dispatch data from data.gov.in.
    Extracts CIL, BCCL, ECL subsidiary dispatch figures impacting SAIL domestic vs import substitution.
    """
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    os.makedirs(os.path.dirname(output_parquet), exist_ok=True)

    records = fetch_data_gov_in_resource(resource_id=resource_id, limit=100, offset=0)
    if not records:
        logger.warning(f"No records returned from data.gov.in resource '{resource_id}'.")
        return None

    df = pd.DataFrame(records)
    df.to_csv(output_csv, index=False)
    df.to_parquet(output_parquet, index=False)

    register_dataset(
        dataset_name="data_gov_in_monthly_coal_dispatch",
        local_path=output_csv,
        source_type="GOVERNMENT_API",
        scope="INDIA_REAL",
        intended_use="Indian domestic coal production and dispatch volumes for import substitution analysis",
        source_url=f"https://api.data.gov.in/resource/{resource_id}",
        rows=len(df),
        columns=list(df.columns),
        limitations="Monthly production and dispatch totals across Indian public coal mining entities (CIL, SCCL, NLCIL)"
    )
    logger.info(f"Successfully ingested and registered {len(df)} live Indian coal dispatch records to {output_csv} and {output_parquet}")
    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    process_all_government_data()
    ingest_live_indian_coal_dispatch()
