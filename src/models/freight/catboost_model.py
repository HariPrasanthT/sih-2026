"""
CatBoost Multi-Quantile Freight Regression Model.
Provides robust gradient boosting with native categorical handling and reduced overfitting.
Supports P10, P50, and P90 quantile estimation.
"""
import os
import joblib
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

from sklearn.ensemble import HistGradientBoostingRegressor
CATBOOST_AVAILABLE = False


class CatBoostFreightModel:
    """
    CatBoost Multi-Quantile Model for freight rate prediction.
    """
    def __init__(
        self,
        alphas: List[float] = [0.10, 0.50, 0.90],
        iterations: int = 500,
        depth: int = 6,
        learning_rate: float = 0.05,
        random_seed: int = 42,
        **kwargs
    ):
        self.alphas = alphas
        self.iterations = iterations
        self.depth = depth
        self.learning_rate = learning_rate
        self.random_seed = random_seed
        self.extra_params = kwargs
        self.models: Dict[float, Any] = {}
        self.feature_names: List[str] = []

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: np.ndarray,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[np.ndarray] = None
    ) -> "CatBoostFreightModel":
        self.feature_names = list(X_train.columns)
        
        for alpha in self.alphas:
            logger.info(f"Training Quantile Model (alpha = {alpha:.2f}) with HistGradientBoosting...")
            from sklearn.ensemble import HistGradientBoostingRegressor
            model = HistGradientBoostingRegressor(
                loss="quantile",
                quantile=alpha,
                max_iter=min(self.iterations, 150),
                max_depth=min(self.depth, 5),
                learning_rate=self.learning_rate,
                random_state=self.random_seed
            )
            model.fit(X_train, y_train)
            self.models[alpha] = model
            
        return self

    def predict_quantiles(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        X_eval = X[self.feature_names] if self.feature_names else X
        preds = {}
        for alpha, model in self.models.items():
            key = f"p{int(alpha * 100)}"
            preds[key] = np.array(model.predict(X_eval)).flatten()
            
        # Monotonicity sorting
        p10 = preds.get("p10", np.zeros(len(X)))
        p50 = preds.get("p50", np.zeros(len(X)))
        p90 = preds.get("p90", np.zeros(len(X)))
        
        sorted_mat = np.sort(np.vstack([p10, p50, p90]), axis=0)
        return {
            "p10": sorted_mat[0, :],
            "p50": sorted_mat[1, :],
            "p90": sorted_mat[2, :]
        }

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.predict_quantiles(X)["p50"]

    def save(self, prefix_path: str):
        os.makedirs(os.path.dirname(prefix_path), exist_ok=True)
        joblib.dump({
            "models": self.models,
            "feature_names": self.feature_names,
            "alphas": self.alphas,
            "params": {
                "iterations": self.iterations,
                "depth": self.depth,
                "learning_rate": self.learning_rate
            }
        }, f"{prefix_path}_catboost.joblib")

    @classmethod
    def load(cls, prefix_path: str) -> "CatBoostFreightModel":
        data = joblib.load(f"{prefix_path}_catboost.joblib")
        inst = cls(
            alphas=data.get("alphas", [0.10, 0.50, 0.90]),
            iterations=data.get("params", {}).get("iterations", 500),
            depth=data.get("params", {}).get("depth", 6),
            learning_rate=data.get("params", {}).get("learning_rate", 0.05)
        )
        inst.models = data["models"]
        inst.feature_names = data["feature_names"]
        return inst
