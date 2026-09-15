import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))
"""
Script 09: Train Transit Duration Regression Model.
"""
import logging
# pyrefly: ignore [missing-import]
from src.data.loaders import load_training_splits
# pyrefly: ignore [missing-import]
from src.models.transit.transit_model import TransitDurationModel
# pyrefly: ignore [missing-import]
from src.evaluation.freight_metrics import evaluate_transit_predictions

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TRANSIT_FEATURES = [
    "route_distance_nm",
    "derived_congestion_index",
    "est_waiting_days",
    "is_monsoon",
    "month_sin",
    "month_cos"
]

if __name__ == "__main__":
    logging.info("STEP 9: Training Transit Duration Model...")
    train_df, val_df, test_df = load_training_splits()
    
    train_clean = train_df.bfill().ffill()
    val_clean = val_df.bfill().ffill()
    
    cols = [c for c in TRANSIT_FEATURES if c in train_clean.columns]
    
    X_train = train_clean[cols]
    y_train = train_clean["transit_days"]
    
    X_val = val_clean[cols]
    y_val = val_clean["transit_days"]
    
    model = TransitDurationModel()
    model.fit(X_train, y_train)
    
    preds_val = model.predict(X_val)
    metrics = evaluate_transit_predictions(y_val.values, preds_val)
    logging.info(f"Transit Model Validation: MAE={metrics['transit_mae_days']} days, R2={metrics['transit_r2']}")
    
    os.makedirs("artifacts/models/transit", exist_ok=True)
    model.save("artifacts/models/transit/transit_model.joblib")
    logging.info("Transit model artifact saved.")
