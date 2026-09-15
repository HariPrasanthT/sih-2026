"""
SIH 26006 Test Suite.
Provides reusable test fixtures, mock vessels, recommendation requests, and port constants.
"""
from typing import Dict, Any, List
import pandas as pd


SAMPLE_VESSEL: Dict[str, Any] = {
    "vessel_id": "VSL_9234567",
    "vessel_name": "MV OCEAN LEADER 1",
    "imo": 9234567,
    "mmsi": 419000137,
    "vessel_class": "Capesize",
    "dwt": 178000,
    "loa_m": 292.0,
    "beam_m": 45.0,
    "draft_m": 18.1,
    "design_speed_knots": 14.5,
    "fuel_consumption_sea_t_day": 48.0,
    "fuel_consumption_port_t_day": 4.5,
    "vessel_age_years": 8,
    "status": "available",
    "current_location": "Bay of Bengal",
    "eta_days_to_load_port": 3.0,
    "daily_hire_rate_usd": 28500.0,
}

SAMPLE_RECOMMENDATION_REQUEST: Dict[str, Any] = {
    "origin_port": "HAY_POINT",
    "destination_port": "DHAMRA",
    "cargo_type": "Coking Coal",
    "cargo_size_tons": 70000.0,
    "ship_date": "2026-09-15",
    "weight_cost": 0.50,
    "weight_speed": 0.30,
    "weight_reliability": 0.20,
    "top_n": 5,
}

SAMPLE_INDIAN_EAST_COAST_PORTS: List[str] = [
    "PARADIP",
    "DHAMRA",
    "VISAKHAPATNAM",
    "GANGAVARAM",
    "KAMARAJAR",
    "HALDIA",
]

SAMPLE_OVERSEAS_LOAD_PORTS: List[str] = [
    "HAY_POINT",
    "GLADSTONE",
    "NEWCASTLE",
    "TANJUNG_BARA",
    "BALIKPAPAN",
    "RICHARDS_BAY",
    "MAPUTO",
]


def get_sample_test_dataframe() -> pd.DataFrame:
    """Return a minimal valid DataFrame matching feature pipeline specifications."""
    return pd.DataFrame([
        {
            "forecast_date": "2024-01-01",
            "origin_port": "HAY_POINT",
            "destination_port": "DHAMRA",
            "cargo_type": "Coking Coal",
            "vessel_class": "Capesize",
            "freight_usd_per_ton": 18.20,
            "transit_days": 14.3,
            "on_time_flag": 1,
            "distance_nm": 4980.0,
            "bdi_index": 1650.0,
            "bunker_vlsfo_usd_ton": 620.0,
            "usd_inr_rate": 83.2,
        }
    ])


__all__ = [
    "SAMPLE_VESSEL",
    "SAMPLE_RECOMMENDATION_REQUEST",
    "SAMPLE_INDIAN_EAST_COAST_PORTS",
    "SAMPLE_OVERSEAS_LOAD_PORTS",
    "get_sample_test_dataframe",
]
