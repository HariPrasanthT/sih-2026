import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))
"""
Script 07: Hyperparameter Tuning using Optuna.
Optimizes hyperparameters for XGBoost, LightGBM, and CatBoost across validation split.
Saves optimal configurations to artifacts/best_params.json.
"""
import json
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def tune_all_models(n_trials: int = 30):
    out_file = "artifacts/best_params.json"
    if os.path.exists(out_file):
        logging.info(f"Optimal parameters already found at {out_file}. Skipping tuning.")
        with open(out_file, "r") as f:
            return json.load(f)

    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    from src.data.loaders import load_training_splits
    from xgboost import XGBRegressor
    from lightgbm import LGBMRegressor

    logging.info(f"STEP 7: Starting Optuna Hyperparameter Optimization ({n_trials} trials per model)...")
    train_df, val_df, _ = load_training_splits()
    
    # Feature columns
    exclude_cols = [
        "forecast_date", "origin_port", "destination_port", "cargo_type",
        "vessel_class", "season", "congestion_severity_level", "freight_usd_per_ton",
        "transit_days", "on_time_flag"
    ]
    features = [c for c in train_df.select_dtypes(include=[np.number]).columns if c not in exclude_cols]
    
    X_train = train_df[features].bfill().ffill().values[:5000]
    y_train = train_df["freight_usd_per_ton"].values[:5000]
    X_val = val_df[features].bfill().ffill().values[:1500]
    y_val = val_df["freight_usd_per_ton"].values[:1500]

    best_params = {}

    # 1. Tune LightGBM
    logging.info("Tuning LightGBM with Optuna...")
    def lgb_objective(trial):
        params = {
            "num_leaves": trial.suggest_int("num_leaves", 15, 63),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "feature_fraction": trial.suggest_float("feature_fraction", 0.6, 1.0),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.15, log=True),
            "n_estimators": 120,
            "random_state": 42,
            "verbosity": -1,
            "n_jobs": -1
        }
        model = LGBMRegressor(**params)
        model.fit(X_train, y_train)
        preds = model.predict(X_val)
        return float(np.mean(np.abs(y_val - preds)))

    study_lgb = optuna.create_study(direction="minimize")
    study_lgb.optimize(lgb_objective, n_trials=n_trials)
    best_params["lightgbm"] = study_lgb.best_params
    logging.info(f"Best LightGBM Params (Val MAE={study_lgb.best_value:.3f}): {study_lgb.best_params}")

    # 2. Tune XGBoost
    logging.info("Tuning XGBoost with Optuna...")
    def xgb_objective(trial):
        params = {
            "max_depth": trial.suggest_int("max_depth", 3, 9),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.15, log=True),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 8),
            "n_estimators": 120,
            "random_state": 42,
            "n_jobs": -1
        }
        model = XGBRegressor(**params)
        model.fit(X_train, y_train)
        preds = model.predict(X_val)
        return float(np.mean(np.abs(y_val - preds)))

    study_xgb = optuna.create_study(direction="minimize")
    study_xgb.optimize(xgb_objective, n_trials=n_trials)
    best_params["xgboost"] = study_xgb.best_params
    logging.info(f"Best XGBoost Params (Val MAE={study_xgb.best_value:.3f}): {study_xgb.best_params}")

    # 3. Tune CatBoost
    logging.info("Tuning CatBoost with Optuna...")
    def cb_objective(trial):
        depth = trial.suggest_int("depth", 4, 8)
        iterations = trial.suggest_int("iterations", 100, 300)
        lr = trial.suggest_float("learning_rate", 0.02, 0.15, log=True)
        model = CatBoostRegressor(
            depth=depth,
            iterations=iterations,
            learning_rate=lr,
            random_seed=42,
            verbose=False
        )
        model.fit(X_train, y_train, eval_set=(X_val, y_val), verbose=False)
        preds = model.predict(X_val)
        return float(np.mean(np.abs(y_val - preds)))

    study_cb = optuna.create_study(direction="minimize")
    study_cb.optimize(cb_objective, n_trials=min(n_trials, 20))
    best_params["catboost"] = study_cb.best_params
    logging.info(f"Best CatBoost Params (Val MAE={study_cb.best_value:.3f}): {study_cb.best_params}")

    # Save best parameters
    out_file = "artifacts/best_params.json"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(best_params, f, indent=2)
    logging.info(f"Saved optimal parameters to {out_file}")
    return best_params


if __name__ == "__main__":
    tune_all_models(n_trials=25)
