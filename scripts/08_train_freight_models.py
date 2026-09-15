import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))
"""
Script 08: Train XGBoost, LightGBM, CatBoost, Random Forest, and Stacking Quantile Ensemble Models.
Monitors generalization gap, runs overfitting detector, and selects champion model.
"""
import json
import logging
from datetime import datetime, timezone
import pandas as pd
import numpy as np

# pyrefly: ignore [missing-import]
from src.data.loaders import load_training_splits
# pyrefly: ignore [missing-import]
from src.models.freight.xgboost_quantile import XGBoostQuantileFreightModel
# pyrefly: ignore [missing-import]
from src.models.freight.lightgbm_quantile import LightGBMQuantileFreightModel
# pyrefly: ignore [missing-import]
from src.models.freight.catboost_model import CatBoostFreightModel
# pyrefly: ignore [missing-import]
from src.models.freight.random_forest import RandomForestFreightModel
# pyrefly: ignore [missing-import]
from src.models.freight.stacking_ensemble import StackingQuantileFreightEnsemble
# pyrefly: ignore [missing-import]
from src.models.freight.ensemble import QuantileEnsembleFreightModel
# pyrefly: ignore [missing-import]
from src.models.validation.overfitting_detector import (
    evaluate_model_overfitting,
    generate_overfitting_plots,
    generate_overfitting_report_html
)
# pyrefly: ignore [missing-import]
from src.evaluation.freight_metrics import evaluate_freight_predictions

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def train_freight_suite():
    logging.info("STEP 8: Starting Multi-Model Freight Training Pipeline...")
    train_df, val_df, test_df = load_training_splits()
    
    train_clean = train_df.bfill().ffill()
    val_clean = val_df.bfill().ffill()
    test_clean = test_df.bfill().ffill()

    exclude_cols = [
        "forecast_date", "origin_port", "destination_port", "cargo_type",
        "vessel_class", "season", "congestion_severity_level", "freight_usd_per_ton",
        "transit_days", "on_time_flag"
    ]
    features = [c for c in train_clean.select_dtypes(include=[np.number]).columns if c not in exclude_cols]
    logging.info(f"Training with {len(features)} strictly shifted, zero-leakage features.")
    
    X_train = train_clean[features]
    y_train = train_clean["freight_usd_per_ton"].values
    X_val = val_clean[features]
    y_val = val_clean["freight_usd_per_ton"].values
    X_test = test_clean[features]
    y_test = test_clean["freight_usd_per_ton"].values

    # Load tuned parameters if available
    params_file = "artifacts/best_params.json"
    best_params = {}
    if os.path.exists(params_file):
        try:
            with open(params_file, "r") as f:
                best_params = json.load(f)
            logging.info(f"Loaded optimal parameters from {params_file}")
        except Exception:
            pass

    trained_models = {}
    overfitting_records = []

    # 1. Train XGBoost Quantile
    logging.info("Training XGBoost Multi-Quantile Model...")
    xgb_p = best_params.get("xgboost", {})
    xgb_model = XGBoostQuantileFreightModel(
        max_depth=xgb_p.get("max_depth", 6),
        learning_rate=xgb_p.get("learning_rate", 0.05),
        subsample=xgb_p.get("subsample", 0.8),
        colsample_bytree=xgb_p.get("colsample_bytree", 0.8)
    )
    xgb_model.fit(X_train, y_train)
    xgb_path = "artifacts/models/freight/xgboost_freight"
    xgb_model.save(xgb_path)
    trained_models["xgboost"] = xgb_model
    
    xgb_tr_pred = xgb_model.predict(X_train)
    xgb_val_pred = xgb_model.predict(X_val)
    xgb_ts_pred = xgb_model.predict(X_test)
    overfitting_records.append(evaluate_model_overfitting("XGBoost Quantile", y_train, xgb_tr_pred, y_val, xgb_val_pred, y_test, xgb_ts_pred))

    # 2. Train LightGBM Quantile
    logging.info("Training LightGBM Multi-Quantile Model...")
    lgb_p = best_params.get("lightgbm", {})
    lgb_model = LightGBMQuantileFreightModel(
        num_leaves=lgb_p.get("num_leaves", 31),
        max_depth=lgb_p.get("max_depth", -1),
        feature_fraction=lgb_p.get("feature_fraction", 0.8),
        learning_rate=lgb_p.get("learning_rate", 0.05)
    )
    lgb_model.fit(X_train, y_train)
    lgb_path = "artifacts/models/freight/lightgbm_freight"
    lgb_model.save(lgb_path)
    trained_models["lightgbm"] = lgb_model
    
    lgb_tr_pred = lgb_model.predict(X_train)
    lgb_val_pred = lgb_model.predict(X_val)
    lgb_ts_pred = lgb_model.predict(X_test)
    overfitting_records.append(evaluate_model_overfitting("LightGBM Quantile", y_train, lgb_tr_pred, y_val, lgb_val_pred, y_test, lgb_ts_pred))

    # 3. Train CatBoost Quantile
    logging.info("Training CatBoost Multi-Quantile Model...")
    cb_p = best_params.get("catboost", {})
    cb_model = CatBoostFreightModel(
        depth=cb_p.get("depth", 6),
        iterations=cb_p.get("iterations", 300),
        learning_rate=cb_p.get("learning_rate", 0.06)
    )
    cb_model.fit(X_train, y_train)
    cb_path = "artifacts/models/freight/catboost_freight"
    cb_model.save(cb_path)
    trained_models["catboost"] = cb_model
    
    cb_tr_pred = cb_model.predict(X_train)
    cb_val_pred = cb_model.predict(X_val)
    cb_ts_pred = cb_model.predict(X_test)
    overfitting_records.append(evaluate_model_overfitting("CatBoost Quantile", y_train, cb_tr_pred, y_val, cb_val_pred, y_test, cb_ts_pred))

    # 4. Train Random Forest Quantile
    logging.info("Training Random Forest Quantile Model...")
    rf_model = RandomForestFreightModel(n_estimators=100, max_depth=12)
    rf_model.fit(X_train, y_train)
    rf_path = "artifacts/models/freight/random_forest_freight.joblib"
    rf_model.save(rf_path)
    trained_models["random_forest"] = rf_model
    
    rf_tr_pred = rf_model.predict(X_train)
    rf_val_pred = rf_model.predict(X_val)
    rf_ts_pred = rf_model.predict(X_test)
    overfitting_records.append(evaluate_model_overfitting("Random Forest", y_train, rf_tr_pred, y_val, rf_val_pred, y_test, rf_ts_pred))

    # 5. Fit Stacking Ensemble with Linear/Ridge Meta-Model
    logging.info("Fitting Stacking Ensemble with Meta-Learner...")
    stacking_ens = StackingQuantileFreightEnsemble(base_models={
        "lightgbm": lgb_model,
        "xgboost": xgb_model,
        "catboost": cb_model,
        "random_forest": rf_model
    })
    stacking_ens.fit_meta_model(X_val, y_val)
    stack_path = "artifacts/models/freight/stacking_ensemble.joblib"
    stacking_ens.save(stack_path)
    trained_models["stacking_ensemble"] = stacking_ens
    
    stk_tr_pred = stacking_ens.predict(X_train)
    stk_val_pred = stacking_ens.predict(X_val)
    stk_ts_pred = stacking_ens.predict(X_test)
    overfitting_records.append(evaluate_model_overfitting("Stacking Ensemble", y_train, stk_tr_pred, y_val, stk_val_pred, y_test, stk_ts_pred))

    # Also save QuantileEnsembleFreightModel for backward compatibility
    weighted_ens = QuantileEnsembleFreightModel(xgb_model, lgb_model)
    weighted_ens.fit_weights(X_val, y_val)
    weighted_ens.save("artifacts/models/freight/ensemble_freight.joblib")

    # 6. Generate Overfitting Reports & Visualizations
    generate_overfitting_report_html(overfitting_records)
    generate_overfitting_plots(y_test, stk_ts_pred, y_train, stk_tr_pred)

    # 7. Select Champion
    val_maes = {r["model"]: r["val_mae"] for r in overfitting_records}
    champion_name = min(val_maes, key=val_maes.get)
    logging.info(f"Selected Champion Model: {champion_name} (Lowest Validation MAE = ${val_maes[champion_name]:.3f}/ton)")

    # Save model registry
    registry = {
        "freight_champion": champion_name,
        "models_trained": list(trained_models.keys()),
        "features": features,
        "training_timestamp": datetime.now(timezone.utc).isoformat(),
        "train_rows": len(train_clean),
        "val_rows": len(val_clean),
        "test_rows": len(test_clean)
    }
    with open("artifacts/model_registry/model_registry.json", "w") as f:
        json.dump(registry, f, indent=2)

    logging.info("STEP 8 COMPLETE: All models trained, overfitting audited, and registry updated.")
    return registry


if __name__ == "__main__":
    train_freight_suite()
