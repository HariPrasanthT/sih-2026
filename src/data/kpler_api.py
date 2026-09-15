"""
Kpler / MarineTraffic Live AIS Maritime API Client.
Implements the Kpler AIS API v2 specification (OpenAPI 3.1.0).
Supports near real-time vessel tracking, ECQL filtering (dwt, vesselType, spatial BBOX),
and GeoJSON FeatureCollection parsing.
"""
import os
import logging
from typing import Dict, Any, List, Optional
import requests

logger = logging.getLogger(__name__)

KPLER_BASE_URL = "https://api.kpler.com"


def _get_kpler_api_key() -> str:
    """Retrieve Kpler / MarineTraffic API key from environment or .env."""
    key = os.environ.get("KPLER_API_KEY", "").strip() or os.environ.get("MARINETRAFFIC_API_KEY", "").strip()
    if not key:
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("KPLER_API_KEY=") or line.startswith("MARINETRAFFIC_API_KEY="):
                        val = line.split("=", 1)[1].strip()
                        if val:
                            return val
    return key


def parse_kpler_feature(feature: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse a single GeoJSON Feature from Kpler /v2/maritime/ais-latest
    into standardized maritime candidate dictionary.
    """
    try:
        props = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coords = geometry.get("coordinates", [0.0, 0.0]) if geometry else [0.0, 0.0]

        lon = coords[0] if len(coords) > 0 else float(props.get("longitude", 0.0))
        lat = coords[1] if len(coords) > 1 else float(props.get("latitude", 0.0))

        return {
            "vessel_uid": props.get("vesselUid"),
            "mmsi": int(props.get("mmsi", 0)),
            "imo": int(props.get("imo", 0)) if props.get("imo") else None,
            "vessel_name": str(props.get("vesselName", "")).strip(),
            "callsign": str(props.get("callsign", "")).strip(),
            "flag": str(props.get("flag", "")).strip(),
            "vessel_type": str(props.get("vesselType", "Bulk Carrier")),
            "dwt": float(props.get("dwt", 0)) if props.get("dwt") else None,
            "grt": float(props.get("grt", 0)) if props.get("grt") else None,
            "draft_m": float(props.get("draught", 0)) if props.get("draught") else None,
            "lat": round(lat, 5),
            "lon": round(lon, 5),
            "sog_knots": float(props.get("sog", 0)) if props.get("sog") is not None else 0.0,
            "cog_deg": float(props.get("cog", 0)) if props.get("cog") is not None else 0.0,
            "heading_deg": int(props.get("heading", 0)) if props.get("heading") is not None else None,
            "destination": str(props.get("destination", "")).strip(),
            "eta": props.get("eta"),
            "pos_dt": props.get("posDt"),
        }
    except Exception as e:
        logger.debug(f"Error parsing Kpler GeoJSON feature: {e}")
        return {}


def query_kpler_latest_vessels(
    filter_expr: str = "vesselType = 'Bulk Carrier'",
    limit: int = 50,
    format_type: str = "json"
) -> List[Dict[str, Any]]:
    """
    Fetch latest vessel positions from Kpler AIS API (/v2/maritime/ais-latest).
    
    Args:
        filter_expr: ECQL filter expression (e.g. "dwt >= 50000 AND vesselType = 'Bulk Carrier'")
        limit: Number of records to return (capped at 1,000,000)
        format_type: "json" (GeoJSON FeatureCollection) or "csv"
        
    Returns:
        List of parsed vessel dictionaries. Gracefully returns empty list if unconfigured or offline.
    """
    api_key = _get_kpler_api_key()
    if not api_key:
        logger.info("Kpler / MarineTraffic API key not configured. Using local candidate fleet.")
        return []

    # Format Authorization header as required by Kpler OpenAPI spec: 'Basic {{API_KEY}}'
    auth_header = api_key if (api_key.startswith("Basic ") or api_key.startswith("Bearer ")) else f"Basic {api_key}"

    headers = {
        "Authorization": auth_header,
        "Accept": "application/json" if format_type == "json" else "text/csv",
        "User-Agent": "SAIL-SIH-Maritime-Forecaster/1.0"
    }

    url = f"{KPLER_BASE_URL}/v2/maritime/ais-latest"
    params = {
        "filter": filter_expr,
        "limit": min(limit, 500),
        "format": format_type
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=12)
        if resp.status_code == 200:
            if format_type == "json":
                data = resp.json()
                features = data.get("features", [])
                vessels = [parse_kpler_feature(f) for f in features]
                return [v for v in vessels if v]
            else:
                import csv
                import io
                reader = csv.DictReader(io.StringIO(resp.text))
                return [r for r in reader]
        else:
            logger.warning(f"Kpler AIS API returned HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        logger.warning(f"Failed to query Kpler AIS API: {e}")

    return []
