"""
AISHub Live Vessel Tracking Client & Parser.
Implements the exact AISHub API specification (MMSI, TSTAMP, LATITUDE, LONGITUDE, SOG, DRAUGHT, DEST).
Parses vessel positions, speed, and drafts with Indian East Coast geofencing.
"""
import os
import io
import csv
import logging
from typing import Dict, Any, List, Optional
import requests
import pandas as pd

logger = logging.getLogger(__name__)

# Canonical bounding box for Indian Ocean / Bay of Bengal
BAY_OF_BENGAL_BBOX = {
    "min_lat": 10.0,
    "max_lat": 23.0,
    "min_lon": 78.0,
    "max_lon": 95.0,
}


def _get_aishub_credentials() -> str:
    """Retrieve AISHub username or API key from environment or .env."""
    key = os.environ.get("AISHUB_API_KEY", "").strip() or os.environ.get("AISHUB_USERNAME", "").strip()
    if not key:
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("AISHUB_API_KEY=") or line.startswith("AISHUB_USERNAME="):
                        val = line.split("=", 1)[1].strip()
                        if val:
                            return val
    return key


def parse_aishub_csv_record(row: Dict[str, str]) -> Dict[str, Any]:
    """
    Parse a single row from AISHub CSV stream matching:
    MMSI, TSTAMP, LATITUDE, LONGITUDE, COG, SOG, HEADING, NAVSTAT, IMO, NAME, CALLSIGN, TYPE, A, B, C, D, DRAUGHT, DEST
    """
    try:
        # Latitude & Longitude (AISHub sometimes returns raw degrees * 600000 or standard float)
        raw_lat = float(row.get("LATITUDE", 0))
        raw_lon = float(row.get("LONGITUDE", 0))
        lat = raw_lat / 600000.0 if abs(raw_lat) > 90.0 else raw_lat
        lon = raw_lon / 600000.0 if abs(raw_lon) > 180.0 else raw_lon

        # SOG in 1/10th knots if > 50, otherwise float
        raw_sog = float(row.get("SOG", 0))
        sog = raw_sog / 10.0 if raw_sog > 50 else raw_sog

        # Draught in 1/10th meters if > 30, otherwise float
        raw_draft = float(row.get("DRAUGHT", 0))
        draft = raw_draft / 10.0 if raw_draft > 30 else raw_draft

        return {
            "mmsi": int(row.get("MMSI", 0)),
            "imo": int(row.get("IMO", 0)) if row.get("IMO") and row.get("IMO") != "0" else None,
            "vessel_name": row.get("NAME", "").strip().strip('"'),
            "callsign": row.get("CALLSIGN", "").strip(),
            "timestamp": row.get("TSTAMP", ""),
            "lat": round(lat, 4),
            "lon": round(lon, 4),
            "sog_knots": round(sog, 1),
            "cog_deg": float(row.get("COG", 0)),
            "heading_deg": int(row.get("HEADING", 0)) if row.get("HEADING") else None,
            "navstat": int(row.get("NAVSTAT", 0)) if row.get("NAVSTAT") else 0,
            "vessel_type": int(row.get("TYPE", 70)) if row.get("TYPE") else 70,
            "draft_m": round(draft, 2),
            "destination": row.get("DEST", "").strip().strip('"'),
        }
    except Exception as e:
        logger.debug(f"Error parsing AISHub record {row}: {e}")
        return {}


def query_live_aishub_vessels(
    min_lat: float = 10.0,
    max_lat: float = 23.0,
    min_lon: float = 78.0,
    max_lon: float = 95.0,
    format_type: str = "csv"
) -> List[Dict[str, Any]]:
    """
    Fetch live vessel positions from AISHub within coordinate bounding box.
    Falls back gracefully if username not yet set or trial limit reached.
    """
    username = _get_aishub_credentials()
    if not username:
        logger.info("AISHUB_API_KEY / username not configured. Using local candidate fleet.")
        return []

    url = (
        f"https://data.aishub.net/ws.php?username={username}&format=1&output={format_type}&compress=0"
        f"&latmin={min_lat}&latmax={max_lat}&lonmin={min_lon}&lonmax={max_lon}"
    )

    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            if format_type == "csv":
                reader = csv.DictReader(io.StringIO(resp.text))
                vessels = [parse_aishub_csv_record(r) for r in reader]
                vessels = [v for v in vessels if v]
                logger.info(f"Retrieved {len(vessels)} live vessels from AISHub.")
                return vessels
            else:
                data = resp.json()
                if isinstance(data, list) and len(data) > 1:
                    records = [parse_aishub_csv_record(r) for r in data[1]]
                    return [r for r in records if r]
        else:
            logger.warning(f"AISHub API returned status {resp.status_code}: {resp.text[:150]}")
    except Exception as e:
        logger.warning(f"Failed to query AISHub API: {e}")

    return []
