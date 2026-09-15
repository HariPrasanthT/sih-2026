"""
Vessel Dynamics and Efficiency Feature Engineering.
Calculates fuel-per-DWT-mile efficiency, draft ratio, and dimensional metrics.
"""
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def build_vessel_features(
    df: pd.DataFrame,
    dwt_col: str = "dwt",
    speed_col: str = "design_speed_knots",
    fuel_col: str = "fuel_consumption_sea_t_day",
    draft_col: str = "draft_m",
    max_draft_col: str = "max_draft_m"
) -> pd.DataFrame:
    """
    Calculate vessel efficiency and dimensional clearance features.
    """
    df_out = df.copy()
    
    if dwt_col in df_out.columns and speed_col in df_out.columns and fuel_col in df_out.columns:
        # Daily nautical miles traveled = speed * 24
        daily_nm = df_out[speed_col] * 24.0
        # Fuel per thousand DWT-mile = (fuel_tonnes / (dwt / 1000 * daily_nm))
        df_out["fuel_per_1000_dwt_nm"] = (df_out[fuel_col] / (df_out[dwt_col] / 1000.0 * daily_nm + 1e-5)).round(4)
        
    if draft_col in df_out.columns and max_draft_col in df_out.columns:
        df_out["draft_underkeel_clearance_m"] = df_out[max_draft_col] - df_out[draft_col]
        df_out["draft_utilization_ratio"] = (df_out[draft_col] / df_out[max_draft_col].replace(0, np.nan)).round(3)
        
    return df_out
