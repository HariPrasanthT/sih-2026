"""
Data Ingestion, Loaders, Port and Vessel Mapping, and Data Quality Assurance.
"""
# pyrefly: ignore [missing-import]
from src.data.loaders import (
    load_port_master,
    load_vessel_master,
    load_port_congestion,
    load_training_splits,
    load_master_dataset,
)
# pyrefly: ignore [missing-import]
from src.data.port_mapping import (
    CANONICAL_PORTS,
    normalize_port_name,
    get_port_constraints,
    export_port_master_tables,
)
# pyrefly: ignore [missing-import]
from src.data.vessel_mapping import (
    VESSEL_CLASSES,
    classify_vessel_by_dwt,
    generate_candidate_fleet,
    export_vessel_master_table,
)
# pyrefly: ignore [missing-import]
from src.data.validation import validate_dataframe_schema
# pyrefly: ignore [missing-import]
from src.data.manifest import register_dataset, load_manifest
# pyrefly: ignore [missing-import]
from src.data.market_api import fetch_live_usd_inr_rate, fetch_live_brent_crude, fetch_fred_series
# pyrefly: ignore [missing-import]
from src.data.government_ingestion import fetch_data_gov_in_resource, ingest_live_indian_coal_dispatch
# pyrefly: ignore [missing-import]
from src.data.weather_api import fetch_live_port_weather
# pyrefly: ignore [missing-import]
from src.data.ais_api import query_live_aishub_vessels, parse_aishub_csv_record
# pyrefly: ignore [missing-import]
from src.data.kpler_api import query_kpler_latest_vessels, parse_kpler_feature

__all__ = [
    "load_port_master",
    "load_vessel_master",
    "load_port_congestion",
    "load_training_splits",
    "load_master_dataset",
    "CANONICAL_PORTS",
    "normalize_port_name",
    "get_port_constraints",
    "export_port_master_tables",
    "VESSEL_CLASSES",
    "classify_vessel_by_dwt",
    "generate_candidate_fleet",
    "export_vessel_master_table",
    "validate_dataframe_schema",
    "register_dataset",
    "load_manifest",
    "fetch_live_usd_inr_rate",
    "fetch_live_brent_crude",
    "fetch_fred_series",
    "fetch_data_gov_in_resource",
    "ingest_live_indian_coal_dispatch",
    "fetch_live_port_weather",
    "query_live_aishub_vessels",
    "parse_aishub_csv_record",
    "query_kpler_latest_vessels",
    "parse_kpler_feature",
]
