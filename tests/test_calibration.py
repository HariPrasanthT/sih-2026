"""
Unit tests for probability calibration and conformal prediction interval coverage evaluation.
"""
import numpy as np
import pytest
# pyrefly: ignore [missing-import]
from src.evaluation.calibration import compute_binary_calibration, evaluate_prediction_interval_calibration


def test_binary_calibration_metrics():
    np.random.seed(42)
    y_true = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 0])
    y_prob = np.array([0.9, 0.1, 0.8, 0.7, 0.2, 0.85, 0.15, 0.3, 0.75, 0.25])
    
    calib = compute_binary_calibration(y_true, y_prob, n_bins=5)
    assert "expected_calibration_error" in calib
    assert "maximum_calibration_error" in calib
    assert "brier_score" in calib
    assert calib["brier_score"] <= 0.15
    assert calib["expected_calibration_error"] >= 0.0


def test_prediction_interval_calibration_passed():
    np.random.seed(42)
    y_true = np.linspace(10, 20, 100)
    # 90 out of 100 true values lie between lower and upper
    lower = y_true - 1.0
    upper = y_true + 1.0
    # Simulate 90% coverage
    lower[0:5] = y_true[0:5] + 0.5   # below lower (violates)
    upper[95:100] = y_true[95:100] - 0.5  # above upper (violates)
    
    res = evaluate_prediction_interval_calibration(y_true, lower, upper, nominal_coverage=0.90)
    assert res["nominal_coverage"] == 0.90
    assert 0.85 <= res["empirical_picp"] <= 0.95
    assert res["is_calibrated"] is True
    assert res["mean_interval_width"] > 0.0


def test_prediction_interval_calibration_failed():
    y_true = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    # Narrow intervals missing targets completely
    lower = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    upper = np.array([2.0, 3.0, 4.0, 5.0, 6.0])
    
    res = evaluate_prediction_interval_calibration(y_true, lower, upper, nominal_coverage=0.90)
    assert res["empirical_picp"] == 0.0
    assert res["is_calibrated"] is False
