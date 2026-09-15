"""
Unit tests for feature engineering, temporal leakage prevention, and Great Circle distances.
"""
import pytest
import pandas as pd
import numpy as np
# pyrefly: ignore [missing-import]
from src.features.freight_features import build_freight_lags_and_rolling
# pyrefly: ignore [missing-import]
from src.features.feature_pipeline import calculate_great_circle_distance_nm, get_route_distance_nm
# pyrefly: ignore [missing-import]
from src.features.temporal_features import build_temporal_features


def test_great_circle_distance():
    # Distance between Hay Point, Australia and Paradip, India should be around 4500-5500 nm
    dist = get_route_distance_nm("HAY_POINT", "PARADIP")
    assert 4000.0 < dist < 6500.0


def test_freight_lags_no_leakage():
    dates = pd.date_range("2026-01-01", periods=10)
    df = pd.DataFrame({
        "forecast_date": dates,
        "freight_usd_per_ton": [10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0]
    })
    
    df_feat = build_freight_lags_and_rolling(df, lags=[1, 3], rolling_windows=[3])
    
    # Check lag 1
    assert np.isnan(df_feat.loc[0, "freight_lag_1d"])
    assert df_feat.loc[1, "freight_lag_1d"] == 10.0
    assert df_feat.loc[2, "freight_lag_1d"] == 12.0
    
    # Check that rolling mean at row t only uses observations before t
    assert np.isnan(df_feat.loc[0, "freight_rolling_mean_3d"])
    assert df_feat.loc[1, "freight_rolling_mean_3d"] == 10.0


def test_temporal_features():
    df = pd.DataFrame({
        "forecast_date": ["2026-07-15", "2026-11-20"]
    })
    df_feat = build_temporal_features(df)
    # July is monsoon
    assert df_feat.loc[0, "is_monsoon"] == 1
    # November is peak procurement, not monsoon
    assert df_feat.loc[1, "is_monsoon"] == 0
    assert df_feat.loc[1, "is_peak_procurement"] == 1
