"""
Market Indicators and Macro Commodity Features.
Generates features from Baltic Dry Index (BDI), bunker fuel prices, USD/INR exchange rates, and crude oil.
"""
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def build_market_features(
    df: pd.DataFrame,
    bunker_col: str = "bunker_vlsfo_usd_ton",
    bdi_col: str = "bdi_index",
    fx_col: str = "usd_inr_rate",
    time_col: str = "forecast_date"
) -> pd.DataFrame:
    """
    Derive rolling averages and momentum for market indicators.
    """
    df_out = df.sort_values(time_col).copy()
    
    # 1. Bunker Fuel (VLSFO) features
    if bunker_col in df_out.columns:
        df_out["bunker_rolling_mean_7d"] = df_out[bunker_col].rolling(7, min_periods=1).mean()
        df_out["bunker_rolling_mean_30d"] = df_out[bunker_col].rolling(30, min_periods=1).mean()
        df_out["bunker_volatility_30d"] = (df_out[bunker_col].rolling(30, min_periods=1).std() / df_out["bunker_rolling_mean_30d"].replace(0, np.nan)).fillna(0.0)
        
    # 2. BDI Market Index features
    if bdi_col in df_out.columns:
        df_out["bdi_rolling_mean_7d"] = df_out[bdi_col].rolling(7, min_periods=1).mean()
        df_out["bdi_rolling_mean_30d"] = df_out[bdi_col].rolling(30, min_periods=1).mean()
        df_out["bdi_momentum_14d"] = df_out[bdi_col] - df_out[bdi_col].shift(14)
        df_out["bdi_pct_change_14d"] = (df_out["bdi_momentum_14d"] / df_out[bdi_col].shift(14).replace(0, np.nan)).fillna(0.0) * 100.0
        
    # 3. FX (USD/INR) features
    if fx_col in df_out.columns:
        df_out["fx_rolling_mean_30d"] = df_out[fx_col].rolling(30, min_periods=1).mean()
        
    return df_out
