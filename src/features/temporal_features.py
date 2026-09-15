"""
Temporal and Calendar Feature Engineering.
Derives calendar, cyclical (sin/cos), Indian monsoon, and peak bulk procurement features.
"""
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def build_temporal_features(
    df: pd.DataFrame,
    date_col: str = "forecast_date"
) -> pd.DataFrame:
    """
    Extract calendar components and cyclical encodings without temporal leakage.
    """
    if date_col not in df.columns:
        return df
        
    df_out = df.copy()
    dt_series = pd.to_datetime(df_out[date_col], errors="coerce")
    
    df_out["year"] = dt_series.dt.year
    df_out["month"] = dt_series.dt.month
    df_out["quarter"] = dt_series.dt.quarter
    df_out["day_of_week"] = dt_series.dt.dayofweek
    df_out["day_of_year"] = dt_series.dt.dayofyear
    df_out["week_of_year"] = dt_series.dt.isocalendar().week.astype(int)
    
    # Cyclical sin/cos encodings
    df_out["month_sin"] = np.sin(2 * np.pi * df_out["month"] / 12.0)
    df_out["month_cos"] = np.cos(2 * np.pi * df_out["month"] / 12.0)
    df_out["day_of_week_sin"] = np.sin(2 * np.pi * df_out["day_of_week"] / 7.0)
    df_out["day_of_week_cos"] = np.cos(2 * np.pi * df_out["day_of_week"] / 7.0)
    
    # Domain-specific Indian Maritime features
    # Southwest Monsoon: June (6) to September (9)
    df_out["is_monsoon"] = df_out["month"].isin([6, 7, 8, 9]).astype(int)
    # Peak dry bulk procurement season (post-monsoon & Q4/Q1 industrial restocking: Oct to Mar)
    df_out["is_peak_procurement"] = df_out["month"].isin([10, 11, 12, 1, 2, 3]).astype(int)
    
    # Seasons: Winter (Jan-Feb), Pre-Monsoon (Mar-May), Monsoon (Jun-Sep), Post-Monsoon (Oct-Dec)
    season_map = {1: "Winter", 2: "Winter", 3: "Pre-Monsoon", 4: "Pre-Monsoon", 5: "Pre-Monsoon",
                  6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
                  10: "Post-Monsoon", 11: "Post-Monsoon", 12: "Post-Monsoon"}
    df_out["season"] = df_out["month"].map(season_map)
    
    # Bay of Bengal Cyclone alert seasons: Pre-monsoon (May-Jun) and Post-monsoon (Oct-Nov)
    df_out["cyclone_alert_season"] = df_out["month"].isin([5, 6, 10, 11]).astype(int)
    
    # Major Indian port operational holidays / reduced gang shifts
    # Republic Day (Jan 26), May Day (May 1), Independence Day (Aug 15), Gandhi Jayanti (Oct 2)
    is_holiday = (
        ((dt_series.dt.month == 1) & (dt_series.dt.day == 26)) |
        ((dt_series.dt.month == 5) & (dt_series.dt.day == 1)) |
        ((dt_series.dt.month == 8) & (dt_series.dt.day == 15)) |
        ((dt_series.dt.month == 10) & (dt_series.dt.day == 2)) |
        ((dt_series.dt.month == 1) & (dt_series.dt.day == 1))
    ).astype(int)
    df_out["is_port_holiday"] = is_holiday
    
    return df_out
