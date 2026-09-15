import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))
"""
Script 11: Calibrate Conformal Prediction Intervals on Validation Split.
Evaluates empirical PICP and mean interval width.
"""
import logging
# pyrefly: ignore [missing-import]
from src.data.loaders import load_training_splits
# pyrefly: ignore [missing-import]
from src.models.freight.xgboost_quantile import XGBoostQuantileFreightModel
# pyrefly: ignore [missing-import]
from src.models.uncertainty.conformal import ConformalPredictionCalibrator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if __name__ == "__main__":
    logging.info("STEP 11: Calibrating Conformal Prediction Uncertainty Bounds...")
    train_df, val_df, test_df = load_training_splits()
    
    val_clean = val_df.bfill().ffill()
    test_clean = test_df.bfill().ffill()
    
    # Load champion freight model
    xgb_path = "artifacts/models/freight/xgboost_freight"
    model = XGBoostQuantileFreightModel.load(xgb_path)
    
    avail_cols = [c for c in model.feature_names if c in val_clean.columns]
    
    X_val = val_clean[avail_cols]
    y_val = val_clean["freight_usd_per_ton"].values
    
    # Predict median P50 on calibration (validation) set
    p50_val = model.predict(X_val)
    
    # Calibrate on validation residuals
    calibrator = ConformalPredictionCalibrator(alpha=0.10, target_picp=0.90, tolerance=0.05)
    calibrator.calibrate(y_val, p50_val)
    
    # Evaluate on held-out test split
    X_test = test_clean[avail_cols]
    y_test = test_clean["freight_usd_per_ton"].values
    p50_test = model.predict(X_test)
    
    low_test, high_test = calibrator.predict_intervals(p50_test)
    cov_metrics = calibrator.evaluate_coverage(y_test, low_test, high_test)
    
    logging.info(
        f"Conformal Test Evaluation:\n"
        f"  - Target PICP:  {cov_metrics['target_picp']*100:.1f}%\n"
        f"  - Empirical PICP: {cov_metrics['empirical_picp']*100:.2f}%\n"
        f"  - Mean Interval Width: ${cov_metrics['mean_interval_width']}/ton\n"
        f"  - Calibration Status: {cov_metrics['calibration_status']}"
    )
    
    os.makedirs("artifacts/conformal", exist_ok=True)
    calibrator.save("artifacts/conformal/conformal_calibrator.joblib")
    logging.info("Conformal calibrator saved.")
