"""
Random Forest Quantile Freight Regression Model.
Uses an ensemble of randomized decision trees with empirical quantile estimation across tree leaf predictions.
"""
import os
import joblib
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

logger = logging.getLogger(__name__)


class RandomForestFreightModel:
    """
    Random Forest model with empirical quantile extraction across estimators.
    """
    def __init__(
        self,
        n_estimators: int = 150,
        max_depth: int = 12,
        min_samples_split: int = 5,
        min_samples_leaf: int = 2,
        random_state: int = 42
    ):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.random_state = random_state
        self.model = RandomForestRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.feature_names: List[str] = []

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: np.ndarray,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[np.ndarray] = None
    ) -> "RandomForestFreightModel":
        self.feature_names = list(X_train.columns)
        self.model.fit(X_train, y_train)
        return self

    def predict_quantiles(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        X_eval = X[self.feature_names] if self.feature_names else X
        # Predict across all individual trees
        tree_preds = np.array([tree.predict(X_eval) for tree in self.model.estimators_])
        
        p10 = np.percentile(tree_preds, 10, axis=0)
        p50 = np.percentile(tree_preds, 50, axis=0)
        p90 = np.percentile(tree_preds, 90, axis=0)
        
        return {
            "p10": p10,
            "p50": p50,
            "p90": p90
        }

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        X_eval = X[self.feature_names] if self.feature_names else X
        return self.model.predict(X_eval)

    def save(self, file_path: str):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        joblib.dump({
            "model": self.model,
            "feature_names": self.feature_names,
            "params": {
                "n_estimators": self.n_estimators,
                "max_depth": self.max_depth
            }
        }, file_path)

    @classmethod
    def load(cls, file_path: str) -> "RandomForestFreightModel":
        data = joblib.load(file_path)
        inst = cls(
            n_estimators=data["params"]["n_estimators"],
            max_depth=data["params"]["max_depth"]
        )
        inst.model = data["model"]
        inst.feature_names = data["feature_names"]
        return inst
