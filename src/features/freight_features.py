"""
Freight Time Series Feature Engineering.
Calculates historical lags, rolling statistics, momentum, and volatility for freight rates.
"""
import logging
from typing import List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def build_freight_lags_and_rolling(
    df: pd.DataFrame,
    target_col: str = "freight_usd_per_ton",
    group_cols: List[str] = None,
    time_col: str = "forecast_date",
    lags: List[int] = [1, 3, 7, 14, 30],
    rolling_windows: List[int] = [7, 30, 90]
) -> pd.DataFrame:
    """
    Generate lag and rolling features on freight rates without temporal leakage.
    Features at row T strictly use observations before T.
    """
    if target_col not in df.columns:
        return df
        
    df_out = df.sort_values(group_cols + [time_col] if group_cols else [time_col]).copy()
    
    # 1. Historical lags
    for lag in lags:
        col_name = f"freight_lag_{lag}d"
        short_col = f"lag_{lag}"
        if group_cols:
            val = df_out.groupby(group_cols)[target_col].shift(lag)
        else:
            val = df_out[target_col].shift(lag)
        df_out[col_name] = val
        df_out[short_col] = val
            
    # 2. Rolling statistics (applied on shifted series to avoid leakage of current day target)
    if group_cols:
        shifted_target = df_out.groupby(group_cols)[target_col].shift(1)
    else:
        shifted_target = df_out[target_col].shift(1)
        
    for window in rolling_windows:
        mean_col = f"freight_rolling_mean_{window}d"
        std_col = f"freight_rolling_std_{window}d"
        short_mean = f"rolling_mean_{window}"
        short_std = f"rolling_std_{window}"
        
        if group_cols:
            m_val = shifted_target.groupby([df_out[c] for c in group_cols]).transform(lambda x: x.rolling(window, min_periods=1).mean())
            s_val = shifted_target.groupby([df_out[c] for c in group_cols]).transform(lambda x: x.rolling(window, min_periods=1).std()).fillna(0.0)
        else:
            m_val = shifted_target.rolling(window, min_periods=1).mean()
            s_val = shifted_target.rolling(window, min_periods=1).std().fillna(0.0)

        df_out[mean_col] = m_val
        df_out[std_col] = s_val
        df_out[short_mean] = m_val
        df_out[short_std] = s_val
            
    # 3. Freight Momentum and Volatility
    if "freight_lag_7d" in df_out.columns and "freight_lag_1d" in df_out.columns:
        df_out["freight_momentum_7d"] = df_out["freight_lag_1d"] - df_out["freight_lag_7d"]
        df_out["freight_pct_change_7d"] = (df_out["freight_momentum_7d"] / df_out["freight_lag_7d"].replace(0, np.nan)).fillna(0.0) * 100.0
        
    if "freight_rolling_std_30d" in df_out.columns and "freight_rolling_mean_30d" in df_out.columns:
        df_out["freight_volatility_30d"] = (df_out["freight_rolling_std_30d"] / df_out["freight_rolling_mean_30d"].replace(0, np.nan)).fillna(0.0)
        
    return df_out
