"""
AIS Derived Maritime Features.
Calculates approaching vessel counts, anchorage density index, ETA pressure, and speed distribution.
"""
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def build_ais_port_density_features(
    df: pd.DataFrame,
    approaching_col: str = "vessels_approaching_count",
    anchorage_col: str = "vessels_anchorage_count"
) -> pd.DataFrame:
    """
    Derive maritime density indices from AIS observations.
    """
    df_out = df.copy()
    
    if approaching_col in df_out.columns and anchorage_col in df_out.columns:
        df_out["ais_total_vessels_in_vicinity"] = df_out[approaching_col] + df_out[anchorage_col]
        df_out["ais_anchorage_to_approach_ratio"] = (df_out[anchorage_col] / (df_out[approaching_col] + 1.0)).fillna(0.0)
        
    return df_out
