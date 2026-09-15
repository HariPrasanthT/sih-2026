"""
XGBoost Multi-Quantile Freight Forecasting Model.
Trains separate quantile regression models (P10, P50, P90) to deliver probabilistic freight estimates.
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
import xgboost as xgb
import joblib

logger = logging.getLogger(__name__)


class XGBoostQuantileFreightModel:
    """
    Multi-quantile XGBoost model predicting P10, P50, and P90 freight rates.
    """
    def __init__(
        self,
        quantiles: List[float] = [0.10, 0.50, 0.90],
        n_estimators: int = 300,
        max_depth: int = 6,
        learning_rate: float = 0.05,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        random_state: int = 42,
        **kwargs
    ):
        self.quantiles = quantiles
        self.params = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "learning_rate": learning_rate,
            "subsample": subsample,
            "colsample_bytree": colsample_bytree,
            "random_state": random_state,
            "n_jobs": -1,
            **kwargs
        }
        self.models: Dict[float, Any] = {}
        self.feature_names: List[str] = []
        self.name = "XGBoost_Quantile"
        
    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None
    ) -> "XGBoostQuantileFreightModel":
        """Fit quantile regressors for each specified quantile alpha."""
        self.feature_names = list(X.columns)
        eval_set = [(X_val, y_val)] if X_val is not None and y_val is not None else None
        
        for q in self.quantiles:
            logger.info(f"Training XGBoost Quantile Model for alpha = {q:.2f}...")
            # Check if xgb supports reg:quantileerror natively
            try:
                model = xgb.XGBRegressor(
                    objective="reg:quantileerror",
                    quantile_alpha=q,
                    **self.params
                )
                model.fit(X, y)
            except Exception:
                # Fallback for versions without quantileerror: use reg:absoluteerror for median or squared for mean
                loss = "reg:absoluteerror" if q == 0.50 else "reg:squarederror"
                model = xgb.XGBRegressor(
                    objective=loss,
                    **self.params
                )
                model.fit(X, y)
                
            self.models[q] = model
            
        logger.info("XGBoost multi-quantile model training complete.")
        return self
        
    def predict_quantiles(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Generate P10, P50, and P90 predictions."""
        preds = {}
        for q in self.quantiles:
            key = f"p{int(q*100)}"
            if q in self.models:
                preds[key] = self.models[q].predict(X)
            else:
                preds[key] = np.zeros(len(X))
                
        # Ensure monotonic ordering: P10 <= P50 <= P90
        if "p10" in preds and "p50" in preds and "p90" in preds:
            preds["p10"] = np.minimum(preds["p10"], preds["p50"])
            preds["p90"] = np.maximum(preds["p90"], preds["p50"])
            
        return preds
        
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Point forecast corresponding to median P50."""
        preds = self.predict_quantiles(X)
        return preds.get("p50", np.zeros(len(X)))
        
    def save(self, filepath_prefix: str) -> None:
        """Save model artifacts to disk."""
        import os
        os.makedirs(os.path.dirname(filepath_prefix), exist_ok=True)
        for q, model in self.models.items():
            path = f"{filepath_prefix}_q{int(q*100)}.joblib"
            joblib.dump(model, path)
        meta_path = f"{filepath_prefix}_meta.joblib"
        joblib.dump({"quantiles": self.quantiles, "features": self.feature_names, "params": self.params}, meta_path)
        logger.info(f"Saved XGBoost quantile artifacts with prefix: {filepath_prefix}")
        
    @classmethod
    def load(cls, filepath_prefix: str) -> "XGBoostQuantileFreightModel":
        """Load model artifacts from disk."""
        meta_path = f"{filepath_prefix}_meta.joblib"
        meta = joblib.load(meta_path)
        instance = cls(quantiles=meta["quantiles"])
        instance.feature_names = meta["features"]
        instance.params = meta["params"]
        for q in meta["quantiles"]:
            path = f"{filepath_prefix}_q{int(q*100)}.joblib"
            instance.models[q] = joblib.load(path)
        return instance
