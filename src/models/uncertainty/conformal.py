"""
Split Conformal Prediction Calibrator.
Transforms point/quantile forecasts into calibrated prediction intervals with finite-sample coverage guarantees.
Calculates PICP (Prediction Interval Coverage Probability) and interval widths.
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
import joblib

logger = logging.getLogger(__name__)


class ConformalPredictionCalibrator:
    """
    Split Conformal Calibrator for regression intervals.
    Computes empirical non-conformity scores on a distinct calibration set.
    """
    def __init__(self, alpha: float = 0.10, target_picp: float = 0.90, tolerance: float = 0.05):
        self.alpha = alpha  # Error rate (0.10 for 90% interval)
        self.target_picp = target_picp
        self.tolerance = tolerance
        self.q_hat: float = 0.0
        self.name = "Split_Conformal_Calibrator"
        
    def calibrate(self, y_true_cal: np.ndarray, y_pred_cal_p50: np.ndarray) -> "ConformalPredictionCalibrator":
        """
        Compute empirical (1 - alpha) quantile of absolute residuals on calibration set.
        q_hat = np.quantile(residuals, ceil((n+1)*(1-alpha))/n)
        """
        residuals = np.abs(y_true_cal - y_pred_cal_p50)
        n = len(residuals)
        
        # Conformal quantile adjustment: (n+1)*(1 - alpha) / n
        level = np.clip(np.ceil((n + 1) * (1.0 - self.alpha)) / n, 0.0, 1.0)
        self.q_hat = float(np.quantile(residuals, level))
        logger.info(f"Conformal calibration completed: n={n}, alpha={self.alpha}, q_hat={self.q_hat:.3f}")
        return self
        
    def predict_intervals(self, y_pred_p50: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate calibrated [lower_bound, upper_bound] intervals around median/point forecast.
        """
        lower = np.maximum(0.0, y_pred_p50 - self.q_hat)
        upper = y_pred_p50 + self.q_hat
        return lower, upper
        
    def evaluate_coverage(self, y_true: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> Dict[str, Any]:
        """
        Evaluate empirical PICP, interval widths, and check against target coverage band.
        """
        covered = (y_true >= lower) & (y_true <= upper)
        picp = float(np.mean(covered))
        widths = upper - lower
        
        mean_width = float(np.mean(widths))
        median_width = float(np.median(widths))
        
        min_acc = self.target_picp - self.tolerance
        max_acc = self.target_picp + self.tolerance
        
        is_passed = (min_acc <= picp <= max_acc)
        status = "PASSED" if is_passed else "FAILED"
        
        metrics = {
            "target_confidence": 1.0 - self.alpha,
            "empirical_picp": round(picp, 4),
            "target_picp": self.target_picp,
            "acceptable_band": [round(min_acc, 3), round(max_acc, 3)],
            "mean_interval_width": round(mean_width, 3),
            "median_interval_width": round(median_width, 3),
            "calibration_status": status,
            "q_hat_margin": round(self.q_hat, 3)
        }
        return metrics
        
    def save(self, filepath: str) -> None:
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({"alpha": self.alpha, "q_hat": self.q_hat, "target_picp": self.target_picp, "tolerance": self.tolerance}, filepath)
        
    @classmethod
    def load(cls, filepath: str) -> "ConformalPredictionCalibrator":
        data = joblib.load(filepath)
        instance = cls(alpha=data["alpha"], target_picp=data["target_picp"], tolerance=data["tolerance"])
        instance.q_hat = data["q_hat"]
        return instance
