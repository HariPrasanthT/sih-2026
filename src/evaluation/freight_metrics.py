"""
Evaluation Metrics Engine for Freight Forecasting, Transit Duration, and Reliability Classification.
Calculates MAE, RMSE, MAPE, SMAPE, R², Pinball Loss, Empirical PICP, and Brier Score.
"""
import logging
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
    precision_recall_curve,
    auc,
    brier_score_loss,
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

logger = logging.getLogger(__name__)


def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Percentage Error (MAPE)."""
    mask = (y_true != 0) & ~np.isnan(y_true) & ~np.isnan(y_pred)
    if not np.any(mask):
        return 0.0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100.0)


def calculate_smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Symmetric Mean Absolute Percentage Error (SMAPE)."""
    denom = (np.abs(y_true) + np.abs(y_pred)) / 2.0
    mask = (denom != 0) & ~np.isnan(y_true) & ~np.isnan(y_pred)
    if not np.any(mask):
        return 0.0
    return float(np.mean(np.abs(y_true[mask] - y_pred[mask]) / denom[mask]) * 100.0)


def calculate_pinball_loss(y_true: np.ndarray, y_pred: np.ndarray, alpha: float) -> float:
    """Pinball (Quantile) Loss for alpha in (0, 1)."""
    err = y_true - y_pred
    return float(np.mean(np.maximum(alpha * err, (alpha - 1.0) * err)))


def evaluate_freight_predictions(
    y_true: np.ndarray,
    y_pred_p50: np.ndarray,
    y_pred_p10: Optional[np.ndarray] = None,
    y_pred_p90: Optional[np.ndarray] = None
) -> Dict[str, Any]:
    """
    Compute comprehensive metrics for freight point and quantile forecasts.
    """
    mae = float(mean_absolute_error(y_true, y_pred_p50))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred_p50)))
    r2 = float(r2_score(y_true, y_pred_p50))
    mape = calculate_mape(y_true, y_pred_p50)
    smape = calculate_smape(y_true, y_pred_p50)
    
    metrics = {
        "mae_usd_ton": round(mae, 3),
        "rmse_usd_ton": round(rmse, 3),
        "mape_pct": round(mape, 2),
        "smape_pct": round(smape, 2),
        "r2_score": round(r2, 4),
        "pinball_loss_p50": round(calculate_pinball_loss(y_true, y_pred_p50, 0.50), 4)
    }
    
    if y_pred_p10 is not None:
        metrics["pinball_loss_p10"] = round(calculate_pinball_loss(y_true, y_pred_p10, 0.10), 4)
        
    if y_pred_p90 is not None:
        metrics["pinball_loss_p90"] = round(calculate_pinball_loss(y_true, y_pred_p90, 0.90), 4)
        
    if y_pred_p10 is not None and y_pred_p90 is not None:
        covered = (y_true >= y_pred_p10) & (y_true <= y_pred_p90)
        picp = float(np.mean(covered))
        widths = y_pred_p90 - y_pred_p10
        metrics["picp_90"] = round(picp, 4)
        metrics["mean_interval_width"] = round(float(np.mean(widths)), 3)
        metrics["median_interval_width"] = round(float(np.median(widths)), 3)
        
    return metrics


def evaluate_transit_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    """Evaluate transit duration estimation."""
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = float(r2_score(y_true, y_pred))
    mape = calculate_mape(y_true, y_pred)
    return {
        "transit_mae_days": round(mae, 3),
        "transit_rmse_days": round(rmse, 3),
        "transit_r2": round(r2, 4),
        "transit_mape_pct": round(mape, 2)
    }


def evaluate_ontime_predictions(y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> Dict[str, Any]:
    """Evaluate on-time probability binary classifier."""
    y_pred = (y_prob >= threshold).astype(int)
    
    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        roc_auc = 0.5
        
    try:
        precision_arr, recall_arr, _ = precision_recall_curve(y_true, y_prob)
        pr_auc = float(auc(recall_arr, precision_arr))
    except Exception:
        pr_auc = 0.5
        
    brier = float(brier_score_loss(y_true, y_prob))
    acc = float(accuracy_score(y_true, y_pred))
    bal_acc = float(balanced_accuracy_score(y_true, y_pred))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    
    return {
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "brier_score": round(brier, 4),
        "accuracy": round(acc, 4),
        "balanced_accuracy": round(bal_acc, 4),
        "f1_score": round(f1, 4)
    }
