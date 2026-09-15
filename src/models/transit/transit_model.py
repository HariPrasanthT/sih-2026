"""
Voyage Transit Duration Prediction Model.
Estimates total transit days from route, vessel, speed, and port operational congestion.
"""
import logging
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import lightgbm as lgb
import joblib

logger = logging.getLogger(__name__)


class TransitDurationModel:
    """
    LightGBM regressor for voyage transit duration in days.
    """
    def __init__(
        self,
        n_estimators: int = 200,
        max_depth: int = 5,
        learning_rate: float = 0.05,
        random_state: int = 42
    ):
        self.params = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "learning_rate": learning_rate,
            "random_state": random_state,
            "n_jobs": -1,
            "verbose": -1
        }
        self.model = lgb.LGBMRegressor(**self.params)
        self.feature_names: List[str] = []
        self.name = "Transit_Duration_LightGBM"
        
    def fit(self, X: pd.DataFrame, y: pd.Series) -> "TransitDurationModel":
        self.feature_names = list(X.columns)
        self.model.fit(X, y)
        logger.info(f"Transit duration model fitted on {len(X)} records.")
        return self
        
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return np.maximum(1.0, self.model.predict(X))
        
    def save(self, filepath: str) -> None:
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({"model": self.model, "features": self.feature_names}, filepath)
        
    @classmethod
    def load(cls, filepath: str) -> "TransitDurationModel":
        data = joblib.load(filepath)
        instance = cls()
        instance.model = data["model"]
        instance.feature_names = data["features"]
        return instance
