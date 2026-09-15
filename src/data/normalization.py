"""
Measurement and Unit Normalization Engine.
Ensures standardized units across freight (USD/ton), capacity (DWT), speed (knots), fuel (t/day), distance (nm), and timestamps (UTC).
"""
import logging
from typing import Any, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def normalize_freight_rate(value: Any, unit: str = "USD_PER_TON") -> Optional[float]:
    """
    Standardize freight rate into USD / metric ton.
    Flags or rejects container units (USD/TEU) without conversion factor.
    """
    if value is None or pd.isna(value):
        return None
    try:
        val = float(value)
        if val <= 0:
            return None
        unit_clean = str(unit).strip().upper()
        if unit_clean in ["USD_PER_TON", "USD/TON", "USD/MT", "$/TON", "$/MT"]:
            return round(val, 2)
        elif unit_clean in ["USD/TEU", "USD_PER_TEU"]:
            logger.warning(f"Incompatible unit '{unit}' for bulk cargo freight rate. Flagged as invalid.")
            return None
        elif unit_clean in ["INR/TON", "INR_PER_TON"]:
            # Approximate USD conversion (1 USD ~ 83 INR)
            return round(val / 83.0, 2)
        return round(val, 2)
    except Exception:
        return None


def normalize_speed_knots(speed: Any) -> Optional[float]:
    """Validate and normalize speed to knots (0 to 30 knots)."""
    if speed is None or pd.isna(speed):
        return None
    try:
        s = float(speed)
        if 0.0 <= s <= 30.0:
            return round(s, 1)
        return None
    except Exception:
        return None


def normalize_draft_meters(draft: Any) -> Optional[float]:
    """Validate and normalize vessel draft in meters (0 to 25m)."""
    if draft is None or pd.isna(draft):
        return None
    try:
        d = float(draft)
        if 2.0 <= d <= 25.0:
            return round(d, 2)
        return None
    except Exception:
        return None


def normalize_timestamp_utc(ts: Any) -> Optional[pd.Timestamp]:
    """Parse and normalize timestamp to UTC timezone."""
    if ts is None or pd.isna(ts):
        return None
    try:
        parsed = pd.to_datetime(ts, utc=True)
        return parsed
    except Exception:
        return None
