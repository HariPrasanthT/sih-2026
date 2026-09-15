"""
Unit tests for Conformal Prediction uncertainty calibration and PICP coverage.
"""
import pytest
import numpy as np
# pyrefly: ignore [missing-import]
from src.models.uncertainty.conformal import ConformalPredictionCalibrator


def test_conformal_calibration():
    np.random.seed(42)
    n_cal = 500
    y_true_cal = np.random.normal(20.0, 3.0, n_cal)
    y_pred_cal = y_true_cal + np.random.normal(0.0, 1.5, n_cal)
    
    calibrator = ConformalPredictionCalibrator(alpha=0.10, target_picp=0.90, tolerance=0.05)
    calibrator.calibrate(y_true_cal, y_pred_cal)
    assert calibrator.q_hat > 0
    
    # Test on held out set
    n_test = 500
    y_true_test = np.random.normal(20.0, 3.0, n_test)
    y_pred_test = y_true_test + np.random.normal(0.0, 1.5, n_test)
    
    low, high = calibrator.predict_intervals(y_pred_test)
    assert np.all(low <= high)
    
    metrics = calibrator.evaluate_coverage(y_true_test, low, high)
    assert 0.85 <= metrics["empirical_picp"] <= 0.95
    assert metrics["calibration_status"] == "PASSED"
