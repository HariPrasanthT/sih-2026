"""
Calibration Evaluation Engine for Probabilistic Forecasts and Classification.
Computes Expected Calibration Error (ECE), Maximum Calibration Error (MCE),
Brier score decomposition, and reliability diagram coordinates.
"""
import logging
from typing import Dict, Any, List, Tuple
import numpy as np
from sklearn.calibration import calibration_curve

logger = logging.getLogger(__name__)


def compute_binary_calibration(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10
) -> Dict[str, Any]:
    """
    Evaluate probability calibration for binary classification (e.g. on-time arrival).
    Returns ECE, MCE, Brier score, and bin-level empirical vs. predicted probabilities.
    """
    y_true = np.asarray(y_true).astype(int)
    y_prob = np.clip(np.asarray(y_prob).astype(float), 0.0, 1.0)
    
    if len(y_true) == 0:
        return {
            "expected_calibration_error": 0.0,
            "maximum_calibration_error": 0.0,
            "brier_score": 0.0,
            "fraction_of_positives": [],
            "mean_predicted_value": []
        }
        
    brier = float(np.mean((y_prob - y_true) ** 2))
    
    # Compute calibration curve
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=n_bins, strategy="uniform")
    
    # Bin assignments for ECE
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    mce = 0.0
    n = len(y_true)
    
    for i in range(n_bins):
        in_bin = (y_prob >= bin_edges[i]) & (y_prob < bin_edges[i + 1] if i < n_bins - 1 else y_prob <= bin_edges[i + 1])
        bin_count = np.sum(in_bin)
        if bin_count > 0:
            bin_acc = np.mean(y_true[in_bin])
            bin_conf = np.mean(y_prob[in_bin])
            diff = abs(bin_acc - bin_conf)
            ece += (bin_count / n) * diff
            mce = max(mce, diff)
            
    return {
        "expected_calibration_error": round(float(ece), 4),
        "maximum_calibration_error": round(float(mce), 4),
        "brier_score": round(float(brier), 4),
        "fraction_of_positives": [round(float(p), 4) for p in prob_true],
        "mean_predicted_value": [round(float(p), 4) for p in prob_pred]
    }


def evaluate_prediction_interval_calibration(
    y_true: np.ndarray,
    lower_bound: np.ndarray,
    upper_bound: np.ndarray,
    nominal_coverage: float = 0.90
) -> Dict[str, Any]:
    """
    Evaluate empirical coverage and calibration quality of prediction intervals.
    """
    y_true = np.asarray(y_true)
    lower = np.asarray(lower_bound)
    upper = np.asarray(upper_bound)
    
    in_interval = (y_true >= lower) & (y_true <= upper)
    picp = float(np.mean(in_interval))
    widths = upper - lower
    mean_width = float(np.mean(widths))
    median_width = float(np.median(widths))
    
    # Coverage error
    coverage_error = picp - nominal_coverage
    
    # Coverage Width-based Criterion (CWC) proxy
    # Penalizes intervals that fail nominal coverage exponentially
    gamma = 50.0  # penalty severity
    penalty = 1.0 if picp >= nominal_coverage else np.exp(-gamma * (picp - nominal_coverage))
    cwc = mean_width * (1.0 + (1.0 if picp < nominal_coverage else 0.0) * np.exp(-gamma * (picp - nominal_coverage)))
    
    return {
        "nominal_coverage": nominal_coverage,
        "empirical_picp": round(picp, 4),
        "coverage_error": round(coverage_error, 4),
        "mean_interval_width": round(mean_width, 2),
        "median_interval_width": round(median_width, 2),
        "is_calibrated": (nominal_coverage - 0.05) <= picp <= (nominal_coverage + 0.05)
    }
