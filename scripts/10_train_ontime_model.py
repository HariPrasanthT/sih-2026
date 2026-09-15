import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))
"""
Script 10: Train and calibrate On-Time Arrival Probability Classifier.
"""
import logging
# pyrefly: ignore [missing-import]
from src.data.loaders import load_training_splits
# pyrefly: ignore [missing-import]
from src.models.ontime.ontime_model import OnTimeArrivalModel
# pyrefly: ignore [missing-import]
from src.evaluation.freight_metrics import evaluate_ontime_predictions

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

ONTIME_FEATURES = [
    "route_distance_nm",
    "derived_congestion_index",
    "est_waiting_days",
    "vessels_approaching_count",
    "vessels_anchorage_count",
    "is_monsoon",
    "month_sin",
    "month_cos"
]

if __name__ == "__main__":
    logging.info("STEP 10: Training Calibrated On-Time Classifier...")
    train_df, val_df, test_df = load_training_splits()
    
    train_clean = train_df.bfill().ffill()
    val_clean = val_df.bfill().ffill()
    
    cols = [c for c in ONTIME_FEATURES if c in train_clean.columns]
    
    X_train = train_clean[cols]
    y_train = train_clean["on_time_flag"]
    
    X_val = val_clean[cols]
    y_val = val_clean["on_time_flag"]
    
    model = OnTimeArrivalModel()
    model.fit(X_train, y_train)
    
    probs_val = model.predict_proba(X_val)
    metrics = evaluate_ontime_predictions(y_val.values, probs_val)
    logging.info(f"On-Time Classifier Validation: ROC-AUC={metrics['roc_auc']}, Brier Score={metrics['brier_score']}, F1={metrics['f1_score']}")
    
    os.makedirs("artifacts/models/ontime", exist_ok=True)
    model.save("artifacts/models/ontime/ontime_model.joblib")
    logging.info("On-Time model artifact saved.")
