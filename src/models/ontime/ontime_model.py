"""
On-Time Arrival Probability Binary Classifier.
Models the probability of arrival within the contract schedule window, evaluating calibration and Brier score.
"""
import logging
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
import joblib

logger = logging.getLogger(__name__)


class OnTimeArrivalModel:
    """
    Calibrated LightGBM classifier predicting the probability of on-time cargo arrival.
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
        self.base_model = lgb.LGBMClassifier(**self.params)
        self.calibrated_model = None
        self.feature_names: List[str] = []
        self.name = "OnTime_LightGBM_Calibrated"
        
    def fit(self, X: pd.DataFrame, y: pd.Series) -> "OnTimeArrivalModel":
        self.feature_names = list(X.columns)
        self.base_model.fit(X, y)
        # Wrap in isotonic / sigmoid calibration
        try:
            from sklearn.calibration import FrozenEstimator
            self.calibrated_model = CalibratedClassifierCV(FrozenEstimator(self.base_model), method="isotonic")
        except (ImportError, TypeError):
            self.calibrated_model = CalibratedClassifierCV(self.base_model, cv="prefit", method="isotonic")
        self.calibrated_model.fit(X, y)
        logger.info(f"On-time classifier fitted on {len(X)} samples.")
        return self
        
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Returns array of probability for class 1 (on-time)."""
        if self.calibrated_model is not None:
            return self.calibrated_model.predict_proba(X)[:, 1]
        return self.base_model.predict_proba(X)[:, 1]
        
    def predict(self, X: pd.DataFrame, threshold: float = 0.5) -> np.ndarray:
        return (self.predict_proba(X) >= threshold).astype(int)
        
    def save(self, filepath: str) -> None:
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({"model": self.calibrated_model or self.base_model, "features": self.feature_names}, filepath)
        
    @classmethod
    def load(cls, filepath: str) -> "OnTimeArrivalModel":
        data = joblib.load(filepath)
        instance = cls()
        instance.calibrated_model = data["model"]
        instance.feature_names = data["features"]
        return instance
