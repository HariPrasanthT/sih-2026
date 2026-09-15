"""
Canonical Port Mapping for Indian East Coast Ports and Key International Origin Ports.
"""
import logging
from typing import Optional, Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)

CANONICAL_PORTS: Dict[str, Dict[str, Any]] = {
    "PARADIP": {
        "aliases": ["PARADIP", "PARADIP PORT", "PARADEEP", "PARADEEP PORT", "INPRT"],
        "country": "India",
        "coast": "East Coast",
        "state": "Odisha",
        "lat": 20.26,
        "lon": 86.68,
        "max_draft_m": 16.0,
        "max_loa_m": 290.0,
        "max_beam_m": 45.0,
        "max_dwt_tonnes": 120000,
        "allowed_vessel_classes": ["Handysize", "Supramax", "Panamax", "Capesize"],
        "avg_turnaround_days": 2.8,
    },
    "VISAKHAPATNAM": {
        "aliases": ["VISAKHAPATNAM", "VIZAG", "VISHAKHAPATNAM", "VISAKHAPATNAM PORT", "INVTZ"],
        "country": "India",
        "coast": "East Coast",
        "state": "Andhra Pradesh",
        "lat": 17.68,
        "lon": 83.28,
        "max_draft_m": 18.1,
        "max_loa_m": 300.0,
        "max_beam_m": 48.0,
        "max_dwt_tonnes": 200000,
        "allowed_vessel_classes": ["Handysize", "Supramax", "Panamax", "Capesize"],
        "avg_turnaround_days": 3.2,
    },
    "DHAMRA": {
        "aliases": ["DHAMRA", "DHAMRA PORT", "DHAMARA", "INDHR"],
        "country": "India",
        "coast": "East Coast",
        "state": "Odisha",
        "lat": 20.80,
        "lon": 86.95,
        "max_draft_m": 18.0,
        "max_loa_m": 320.0,
        "max_beam_m": 50.0,
        "max_dwt_tonnes": 180000,
        "allowed_vessel_classes": ["Handysize", "Supramax", "Panamax", "Capesize"],
        "avg_turnaround_days": 2.1,
    },
    "GANGAVARAM": {
        "aliases": ["GANGAVARAM", "GANGAVARAM PORT", "INGGV"],
        "country": "India",
        "coast": "East Coast",
        "state": "Andhra Pradesh",
        "lat": 17.61,
        "lon": 83.23,
        "max_draft_m": 19.5,
        "max_loa_m": 320.0,
        "max_beam_m": 50.0,
        "max_dwt_tonnes": 200000,
        "allowed_vessel_classes": ["Handysize", "Supramax", "Panamax", "Capesize"],
        "avg_turnaround_days": 2.4,
    },
    "KAMARAJAR": {
        "aliases": ["KAMARAJAR", "KAMARAJAR PORT", "ENNORE", "ENNORE PORT", "INKRP"],
        "country": "India",
        "coast": "East Coast",
        "state": "Tamil Nadu",
        "lat": 13.25,
        "lon": 80.33,
        "max_draft_m": 15.5,
        "max_loa_m": 275.0,
        "max_beam_m": 45.0,
        "max_dwt_tonnes": 90000,
        "allowed_vessel_classes": ["Handysize", "Supramax", "Panamax"],
        "avg_turnaround_days": 2.5,
    },
    "CHENNAI": {
        "aliases": ["CHENNAI", "CHENNAI PORT", "MADRAS", "INMAA"],
        "country": "India",
        "coast": "East Coast",
        "state": "Tamil Nadu",
        "lat": 13.08,
        "lon": 80.30,
        "max_draft_m": 16.5,
        "max_loa_m": 290.0,
        "max_beam_m": 45.0,
        "max_dwt_tonnes": 110000,
        "allowed_vessel_classes": ["Handysize", "Supramax", "Panamax"],
        "avg_turnaround_days": 2.9,
    },
    "HALDIA": {
        "aliases": ["HALDIA", "HALDIA DOCK COMPLEX", "HALDIA PORT", "INHAL"],
        "country": "India",
        "coast": "East Coast",
        "state": "West Bengal",
        "lat": 22.02,
        "lon": 88.06,
        "max_draft_m": 8.5,
        "max_loa_m": 230.0,
        "max_beam_m": 32.2,
        "max_dwt_tonnes": 45000,
        "allowed_vessel_classes": ["Handysize", "Supramax"],
        "avg_turnaround_days": 3.8,
    },
    "KOLKATA": {
        "aliases": ["KOLKATA", "KOLKATA PORT", "CALCUTTA", "SMP KOLKATA", "INCCU"],
        "country": "India",
        "coast": "East Coast",
        "state": "West Bengal",
        "lat": 22.54,
        "lon": 88.32,
        "max_draft_m": 7.5,
        "max_loa_m": 180.0,
        "max_beam_m": 26.0,
        "max_dwt_tonnes": 25000,
        "allowed_vessel_classes": ["Handysize"],
        "avg_turnaround_days": 4.5,
    },
    "GOPALPUR": {
        "aliases": ["GOPALPUR", "GOPALPUR PORT", "INGPR"],
        "country": "India",
        "coast": "East Coast",
        "state": "Odisha",
        "lat": 19.30,
        "lon": 84.97,
        "max_draft_m": 14.5,
        "max_loa_m": 250.0,
        "max_beam_m": 38.0,
        "max_dwt_tonnes": 75000,
        "allowed_vessel_classes": ["Handysize", "Supramax", "Panamax"],
        "avg_turnaround_days": 2.6,
    },
    # Major International Origins
    "HAY_POINT": {
        "aliases": ["HAY POINT", "DALRYMPLE BAY", "DBCT", "AUHPT"],
        "country": "Australia",
        "lat": -21.28,
        "lon": 149.30,
        "max_draft_m": 19.0,
        "max_loa_m": 350.0,
        "max_beam_m": 55.0,
        "max_dwt_tonnes": 220000,
        "allowed_vessel_classes": ["Panamax", "Capesize"],
    },
    "GLADSTONE": {
        "aliases": ["GLADSTONE", "PORT OF GLADSTONE", "AUGLT"],
        "country": "Australia",
        "lat": -23.83,
        "lon": 151.27,
        "max_draft_m": 18.5,
        "max_loa_m": 330.0,
        "max_beam_m": 54.0,
        "max_dwt_tonnes": 200000,
        "allowed_vessel_classes": ["Panamax", "Capesize"],
    },
    "NEWCASTLE": {
        "aliases": ["NEWCASTLE", "PORT WARATAH", "PWCS", "AUNTL"],
        "country": "Australia",
        "lat": -32.92,
        "lon": 151.78,
        "max_draft_m": 16.5,
        "max_loa_m": 300.0,
        "max_beam_m": 50.0,
        "max_dwt_tonnes": 180000,
        "allowed_vessel_classes": ["Panamax", "Capesize"],
    },
    "TANJUNG_BARA": {
        "aliases": ["TANJUNG BARA", "SANGATTA", "KPC TANJUNG BARA", "IDTJB"],
        "country": "Indonesia",
        "lat": 0.53,
        "lon": 117.65,
        "max_draft_m": 17.5,
        "max_loa_m": 310.0,
        "max_beam_m": 50.0,
        "max_dwt_tonnes": 180000,
        "allowed_vessel_classes": ["Supramax", "Panamax", "Capesize"],
    },
    "BALIKPAPAN": {
        "aliases": ["BALIKPAPAN", "IDBPN"],
        "country": "Indonesia",
        "lat": -1.27,
        "lon": 116.83,
        "max_draft_m": 14.5,
        "max_loa_m": 250.0,
        "max_beam_m": 40.0,
        "max_dwt_tonnes": 80000,
        "allowed_vessel_classes": ["Handysize", "Supramax", "Panamax"],
    },
    "TABONEO": {
        "aliases": ["TABONEO", "BANJARMASIN ANCHORAGE", "IDTBO"],
        "country": "Indonesia",
        "lat": -3.73,
        "lon": 114.48,
        "max_draft_m": 15.0,
        "max_loa_m": 260.0,
        "max_beam_m": 43.0,
        "max_dwt_tonnes": 90000,
        "allowed_vessel_classes": ["Handysize", "Supramax", "Panamax"],
    },
    "MAPUTO": {
        "aliases": ["MAPUTO", "MATOLA", "MZMPM"],
        "country": "Mozambique",
        "lat": -25.97,
        "lon": 32.58,
        "max_draft_m": 14.2,
        "max_loa_m": 250.0,
        "max_beam_m": 38.0,
        "max_dwt_tonnes": 80000,
        "allowed_vessel_classes": ["Handysize", "Supramax", "Panamax"],
    },
    "RICHARDS_BAY": {
        "aliases": ["RICHARDS BAY", "RBCT", "ZARCB"],
        "country": "South Africa",
        "lat": -28.80,
        "lon": 32.05,
        "max_draft_m": 19.0,
        "max_loa_m": 350.0,
        "max_beam_m": 55.0,
        "max_dwt_tonnes": 220000,
        "allowed_vessel_classes": ["Panamax", "Capesize"],
    },
    "UST_LUGA": {
        "aliases": ["UST-LUGA", "UST LUGA", "RUULU"],
        "country": "Russia",
        "lat": 59.68,
        "lon": 28.32,
        "max_draft_m": 17.5,
        "max_loa_m": 300.0,
        "max_beam_m": 48.0,
        "max_dwt_tonnes": 160000,
        "allowed_vessel_classes": ["Supramax", "Panamax", "Capesize"],
    },
    "NORFOLK": {
        "aliases": ["NORFOLK", "HAMPTON ROADS", "LAMBERTS POINT", "USORF"],
        "country": "United States",
        "lat": 36.85,
        "lon": -76.30,
        "max_draft_m": 15.2,
        "max_loa_m": 300.0,
        "max_beam_m": 48.0,
        "max_dwt_tonnes": 150000,
        "allowed_vessel_classes": ["Panamax", "Capesize"],
    }
}

# Inverted index for fast normalization lookup
ALIAS_MAP: Dict[str, str] = {}
for canonical, data in CANONICAL_PORTS.items():
    ALIAS_MAP[canonical.upper()] = canonical
    for alias in data["aliases"]:
        ALIAS_MAP[alias.upper()] = canonical


def normalize_port_name(raw_name: Optional[str]) -> Optional[str]:
    """
    Resolve port name variations into canonical port identifier.
    Returns canonical name string if recognized, otherwise None (logging unknown).
    """
    if raw_name is None or pd.isna(raw_name):
        return None
    cleaned = str(raw_name).strip().upper()
    if cleaned in ALIAS_MAP:
        return ALIAS_MAP[cleaned]
    
    # Try partial clean
    cleaned_simple = cleaned.replace("PORT OF ", "").replace(" PORT", "").strip()
    if cleaned_simple in ALIAS_MAP:
        return ALIAS_MAP[cleaned_simple]
    
    logger.warning(f"Unknown port name encountered during normalization: '{raw_name}'")
    return None


def get_port_constraints(port_name: str) -> Optional[Dict[str, Any]]:
    """Retrieve physical and operational constraints for a given port."""
    canonical = normalize_port_name(port_name)
    if canonical and canonical in CANONICAL_PORTS:
        return CANONICAL_PORTS[canonical]
    return None


def export_port_master_tables(output_dir: str = "data/processed/ports") -> None:
    """Generate port_master.parquet and port_constraints.parquet."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    records = []
    for canonical, details in CANONICAL_PORTS.items():
        records.append({
            "port_code": canonical,
            "port_name": canonical,
            "canonical_name": canonical,
            "country": details.get("country", ""),
            "coast": details.get("coast", "International"),
            "state": details.get("state", ""),
            "latitude": details.get("lat", 0.0),
            "longitude": details.get("lon", 0.0),
            "max_draft_m": details.get("max_draft_m", 15.0),
            "max_loa_m": details.get("max_loa_m", 280.0),
            "max_beam_m": details.get("max_beam_m", 45.0),
            "max_dwt_tonnes": details.get("max_dwt_tonnes", 100000),
            "allowed_vessel_classes": ",".join(details.get("allowed_vessel_classes", [])),
            "avg_turnaround_days": details.get("avg_turnaround_days", 3.0),
        })
    
    df = pd.DataFrame(records)
    master_path = os.path.join(output_dir, "port_master.parquet")
    constraints_path = os.path.join(output_dir, "port_constraints.parquet")
    
    df.to_parquet(master_path, index=False)
    df.to_parquet(constraints_path, index=False)
    logger.info(f"Port tables exported to {master_path} and {constraints_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    export_port_master_tables()
