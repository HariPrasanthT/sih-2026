"""
Naive and Moving Average Baseline Models for Freight Forecasting Benchmark.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any


class NaiveLastValueModel:
    """Predicts target value equal to the most recent historical observation."""
    def __init__(self, lag_col: str = "freight_lag_1d"):
        self.lag_col = lag_col
        self.name = "Naive_Last_Value"
        
    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        return self
        
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.lag_col in X.columns:
            return X[self.lag_col].fillna(X[self.lag_col].mean()).values
        # Fallback to mean if column missing
        return np.full(len(X), 15.0)


class MovingAverageModel:
    """Predicts target value equal to 7-day or 30-day moving average."""
    def __init__(self, window_col: str = "freight_rolling_mean_7d"):
        self.window_col = window_col
        self.name = f"Moving_Average_{window_col}"
        
    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        return self
        
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.window_col in X.columns:
            return X[self.window_col].fillna(X[self.window_col].mean()).values
        return np.full(len(X), 15.0)


class SeasonalNaiveModel:
    """Predicts target value equal to observation from lag-30."""
    def __init__(self, lag_col: str = "freight_lag_30d"):
        self.lag_col = lag_col
        self.name = "Seasonal_Naive_30d"
        
    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        return self
        
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.lag_col in X.columns:
            return X[self.lag_col].fillna(X[self.lag_col].mean()).values
        return np.full(len(X), 15.0)
