"""
Quantile Model Ensemble.
Optimizes combination weights on validation data to minimize validation pinball loss.
"""
import logging
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import joblib

logger = logging.getLogger(__name__)


def pinball_loss(y_true: np.ndarray, y_pred: np.ndarray, alpha: float) -> float:
    """Calculate pinball (quantile) loss for a given quantile level alpha."""
    err = y_true - y_pred
    return float(np.mean(np.maximum(alpha * err, (alpha - 1.0) * err)))


class QuantileEnsembleFreightModel:
    """
    Weighted Ensemble of XGBoost and LightGBM Quantile Models.
    Weights are empirically fitted on validation data using SLSQP optimization.
    """
    def __init__(self, xgb_model: Any, lgb_model: Any, quantiles: List[float] = [0.10, 0.50, 0.90]):
        self.xgb_model = xgb_model
        self.lgb_model = lgb_model
        self.quantiles = quantiles
        self.weights: Dict[float, Tuple[float, float]] = {}  # alpha -> (w_xgb, w_lgb)
        self.name = "Quantile_Ensemble"
        
    def fit_weights(self, X_val: pd.DataFrame, y_val: Any) -> "QuantileEnsembleFreightModel":
        """Learn optimal convex weights per quantile alpha on validation data."""
        xgb_preds = self.xgb_model.predict_quantiles(X_val)
        lgb_preds = self.lgb_model.predict_quantiles(X_val)
        y_true = y_val.values if hasattr(y_val, "values") else np.asarray(y_val)
        
        for q in self.quantiles:
            key = f"p{int(q*100)}"
            p_xgb = xgb_preds[key]
            p_lgb = lgb_preds[key]
            
            # Optimize w: minimize pinball_loss(y, w*p_xgb + (1-w)*p_lgb)
            def obj(w):
                p_ens = w[0] * p_xgb + (1.0 - w[0]) * p_lgb
                return pinball_loss(y_true, p_ens, q)
                
            res = minimize(obj, [0.5], bounds=[(0.0, 1.0)], method="SLSQP")
            w_xgb = float(res.x[0]) if res.success else 0.5
            w_lgb = float(1.0 - w_xgb)
            self.weights[q] = (w_xgb, w_lgb)
            logger.info(f"Ensemble weights for alpha={q:.2f}: XGBoost={w_xgb:.3f}, LightGBM={w_lgb:.3f}")
            
        return self
        
    def predict_quantiles(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Generate combined quantile predictions."""
        xgb_preds = self.xgb_model.predict_quantiles(X)
        lgb_preds = self.lgb_model.predict_quantiles(X)
        
        preds = {}
        for q in self.quantiles:
            key = f"p{int(q*100)}"
            w_xgb, w_lgb = self.weights.get(q, (0.5, 0.5))
            preds[key] = w_xgb * xgb_preds[key] + w_lgb * lgb_preds[key]
            
        # Ensure monotonic order
        if "p10" in preds and "p50" in preds and "p90" in preds:
            preds["p10"] = np.minimum(preds["p10"], preds["p50"])
            preds["p90"] = np.maximum(preds["p90"], preds["p50"])
            
        return preds
        
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Point forecast corresponding to median P50."""
        preds = self.predict_quantiles(X)
        return preds.get("p50", np.zeros(len(X)))
        
    def save(self, filepath: str) -> None:
        """Save ensemble weights and metadata."""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({"weights": self.weights, "quantiles": self.quantiles}, filepath)
