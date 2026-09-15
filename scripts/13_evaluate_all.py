import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))
"""
Script 13: Comprehensive End-to-End Evaluation, SHAP Report, and Final Model Reporting.
Runs on held-out 2026 test split.
Generates:
- reports/evaluation/final_model_report.md
- reports/shap_report.html
- reports/figures/ (6 diagnostic figures)
- artifacts/model_registry/evaluation_metrics.json
"""
import json
import logging
import pandas as pd
import numpy as np

# pyrefly: ignore [missing-import]
from src.data.loaders import load_training_splits
# pyrefly: ignore [missing-import]
from src.models.baselines.naive import NaiveLastValueModel, MovingAverageModel, SeasonalNaiveModel
# pyrefly: ignore [missing-import]
from src.models.freight.xgboost_quantile import XGBoostQuantileFreightModel
# pyrefly: ignore [missing-import]
from src.models.freight.lightgbm_quantile import LightGBMQuantileFreightModel
# pyrefly: ignore [missing-import]
from src.models.freight.catboost_model import CatBoostFreightModel
# pyrefly: ignore [missing-import]
from src.models.freight.random_forest import RandomForestFreightModel
# pyrefly: ignore [missing-import]
from src.models.freight.ensemble import QuantileEnsembleFreightModel
# pyrefly: ignore [missing-import]
from src.models.transit.transit_model import TransitDurationModel
# pyrefly: ignore [missing-import]
from src.models.ontime.ontime_model import OnTimeArrivalModel
# pyrefly: ignore [missing-import]
from src.models.uncertainty.conformal import ConformalPredictionCalibrator
# pyrefly: ignore [missing-import]
from src.evaluation.report import generate_evaluation_report, generate_evaluation_figures
# pyrefly: ignore [missing-import]
from src.evaluation.calibration import compute_binary_calibration
# pyrefly: ignore [missing-import]
from src.explainability.shap_explainer import FreightSHAPExplainer
# pyrefly: ignore [missing-import]
from src.evaluation.html_reports import generate_shap_report_html
# pyrefly: ignore [missing-import]
from src.evaluation.freight_metrics import (
    evaluate_freight_predictions,
    evaluate_transit_predictions,
    evaluate_ontime_predictions
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def run_full_evaluation():
    logging.info("STEP 13: Running Full Held-Out 2026 Test Evaluation...")
    train_df, val_df, test_df = load_training_splits()
    
    test_clean = test_df.bfill().ffill()
    val_clean = val_df.bfill().ffill()
    
    y_test_fr = test_clean["freight_usd_per_ton"].values
    y_test_tr = test_clean["transit_days"].values
    y_test_ot = test_clean["on_time_flag"].values
    
    # 1. Evaluate Baselines
    naive_m = evaluate_freight_predictions(y_test_fr, NaiveLastValueModel().predict(test_clean))
    naive_m["model"] = "Naive (Last-Value)"
    
    ma_col = "rolling_mean_7" if "rolling_mean_7" in test_clean.columns else "freight_rolling_mean_7d"
    ma7_m = evaluate_freight_predictions(y_test_fr, MovingAverageModel(ma_col).predict(test_clean))
    ma7_m["model"] = "Moving Average (7-Day)"
    
    snaive_col = "lag_30" if "lag_30" in test_clean.columns else "freight_lag_30d"
    snaive_m = evaluate_freight_predictions(y_test_fr, SeasonalNaiveModel(snaive_col).predict(test_clean))
    snaive_m["model"] = "Seasonal Naive (30-Day)"
    
    # 2. Load and Evaluate ML Freight Models
    xgb_path = "artifacts/models/freight/xgboost_freight"
    xgb_model = XGBoostQuantileFreightModel.load(xgb_path)
    xgb_cols = [c for c in xgb_model.feature_names if c in test_clean.columns]
    xgb_preds = xgb_model.predict_quantiles(test_clean[xgb_cols])
    xgb_m = evaluate_freight_predictions(y_test_fr, xgb_preds["p50"], xgb_preds["p10"], xgb_preds["p90"])
    xgb_m["model"] = "XGBoost Quantile"
    
    lgb_path = "artifacts/models/freight/lightgbm_freight"
    lgb_model = LightGBMQuantileFreightModel.load(lgb_path)
    lgb_cols = [c for c in lgb_model.feature_names if c in test_clean.columns]
    lgb_preds = lgb_model.predict_quantiles(test_clean[lgb_cols])
    lgb_m = evaluate_freight_predictions(y_test_fr, lgb_preds["p50"], lgb_preds["p10"], lgb_preds["p90"])
    lgb_m["model"] = "LightGBM Quantile"

    # CatBoost
    cb_path = "artifacts/models/freight/catboost_freight"
    cb_m = None
    if os.path.exists(f"{cb_path}_catboost.joblib"):
        cb_model = CatBoostFreightModel.load(cb_path)
        cb_cols = [c for c in cb_model.feature_names if c in test_clean.columns]
        cb_preds = cb_model.predict_quantiles(test_clean[cb_cols])
        cb_m = evaluate_freight_predictions(y_test_fr, cb_preds["p50"], cb_preds["p10"], cb_preds["p90"])
        cb_m["model"] = "CatBoost Quantile"

    # Random Forest
    rf_path = "artifacts/models/freight/random_forest_freight.joblib"
    rf_m = None
    if os.path.exists(rf_path):
        rf_model = RandomForestFreightModel.load(rf_path)
        rf_cols = [c for c in rf_model.feature_names if c in test_clean.columns]
        rf_preds = rf_model.predict_quantiles(test_clean[rf_cols])
        rf_m = evaluate_freight_predictions(y_test_fr, rf_preds["p50"], rf_preds["p10"], rf_preds["p90"])
        rf_m["model"] = "Random Forest Quantile"
    
    # Stacking / Weighted Ensemble
    ensemble = QuantileEnsembleFreightModel(xgb_model, lgb_model)
    ens_path = "artifacts/models/freight/ensemble_freight.joblib"
    if os.path.exists(ens_path):
        import joblib
        ens_data = joblib.load(ens_path)
        ensemble.weights = ens_data.get("weights", ensemble.weights)
    ens_preds = ensemble.predict_quantiles(test_clean[xgb_cols])
    ens_m = evaluate_freight_predictions(y_test_fr, ens_preds["p50"], ens_preds["p10"], ens_preds["p90"])
    ens_m["model"] = "Quantile Ensemble"
    
    # Stacking Ensemble with Meta-Learner
    stack_m = None
    stack_path = "artifacts/models/freight/stacking_ensemble.joblib"
    if os.path.exists(stack_path) and cb_m is not None and rf_m is not None:
        try:
            # pyrefly: ignore [missing-import]
            from src.models.freight.stacking_ensemble import StackingQuantileFreightEnsemble
            base_models = {
                "lightgbm": lgb_model,
                "xgboost": xgb_model,
                "catboost": cb_model,
                "random_forest": rf_model
            }
            stack_ens = StackingQuantileFreightEnsemble.load(stack_path, base_models)
            stack_preds = stack_ens.predict_quantiles(test_clean[xgb_cols])
            stack_m = evaluate_freight_predictions(y_test_fr, stack_preds["p50"], stack_preds["p10"], stack_preds["p90"])
            stack_m["model"] = "Stacking Ensemble (Meta-Learner)"
        except Exception as e:
            logging.warning(f"Could not evaluate stacking ensemble: {e}")
            stack_m = None

    model_comparison = [naive_m, ma7_m, snaive_m, xgb_m, lgb_m]
    if cb_m:
        model_comparison.append(cb_m)
    if rf_m:
        model_comparison.append(rf_m)
    model_comparison.append(ens_m)
    if stack_m:
        model_comparison.append(stack_m)
    
    # 3. Evaluate Transit Model
    tr_path = "artifacts/models/transit/transit_model.joblib"
    tr_model = TransitDurationModel.load(tr_path)
    tr_cols = [c for c in tr_model.feature_names if c in test_clean.columns]
    tr_preds = tr_model.predict(test_clean[tr_cols])
    tr_metrics = evaluate_transit_predictions(y_test_tr, tr_preds)
    
    # 4. Evaluate On-Time Model
    ot_path = "artifacts/models/ontime/ontime_model.joblib"
    ot_model = OnTimeArrivalModel.load(ot_path)
    ot_cols = [c for c in ot_model.feature_names if c in test_clean.columns]
    ot_probs = ot_model.predict_proba(test_clean[ot_cols])
    ot_metrics = evaluate_ontime_predictions(y_test_ot, ot_probs)
    
    # 5. Evaluate Conformal Coverage
    conf_path = "artifacts/conformal/conformal_calibrator.joblib"
    conf_cal = ConformalPredictionCalibrator.load(conf_path)
    low_test, high_test = conf_cal.predict_intervals(xgb_preds["p50"])
    conf_metrics = conf_cal.evaluate_coverage(y_test_fr, low_test, high_test)
    
    # 6. Route-wise evaluation
    route_metrics = []
    test_clean["pred_p50"] = xgb_preds["p50"]
    for (orig, dest), grp in test_clean.groupby(["origin_port", "destination_port"]):
        mae_r = float(np.mean(np.abs(grp["freight_usd_per_ton"] - grp["pred_p50"])))
        mape_r = float(np.mean(np.abs((grp["freight_usd_per_ton"] - grp["pred_p50"]) / grp["freight_usd_per_ton"])) * 100.0)
        cargo = str(grp["cargo_type"].iloc[0])
        vclass = str(grp["vessel_class"].iloc[0])
        route_metrics.append({
            "route": f"{orig} -> {dest}",
            "cargo": cargo,
            "vclass": vclass,
            "mae": round(mae_r, 2),
            "mape": round(mape_r, 1),
            "samples": len(grp)
        })
        
    # 7. Vessel-class evaluation
    vclass_metrics = []
    dwt_ranges = {"Capesize": "100k - 350k DWT", "Panamax": "65k - 99k DWT", "Supramax": "40k - 64k DWT", "Handysize": "10k - 39k DWT"}
    for vclass, grp in test_clean.groupby("vessel_class"):
        mae_v = float(np.mean(np.abs(grp["freight_usd_per_ton"] - grp["pred_p50"])))
        mape_v = float(np.mean(np.abs((grp["freight_usd_per_ton"] - grp["pred_p50"]) / grp["freight_usd_per_ton"])) * 100.0)
        vclass_metrics.append({
            "class": vclass,
            "dwt_range": dwt_ranges.get(vclass, "-"),
            "mae": round(mae_v, 2),
            "mape": round(mape_v, 1)
        })
        
    # 8. SHAP & Diagnostics
    explainer = FreightSHAPExplainer(xgb_model, xgb_cols)
    feat_imps = explainer.get_global_importance(top_k=20)
    generate_shap_report_html(feat_imps, output_path="reports/shap_report.html")

    calib_stats = compute_binary_calibration(y_test_ot, ot_probs)

    generate_evaluation_figures(
        y_test=y_test_fr,
        pred_p50=xgb_preds["p50"],
        pred_p10=xgb_preds["p10"],
        pred_p90=xgb_preds["p90"],
        route_metrics=route_metrics,
        feature_importances=feat_imps[:10],
        prob_true=calib_stats.get("fraction_of_positives"),
        prob_pred=calib_stats.get("mean_predicted_value"),
        output_dir="reports/figures"
    )

    dataset_summary = {
        "train_rows": len(train_df),
        "val_rows": len(val_df),
        "test_rows": len(test_df),
        "date_range": f"{test_clean['forecast_date'].min().strftime('%Y-%m-%d')} to {test_clean['forecast_date'].max().strftime('%Y-%m-%d')}"
    }

    generate_evaluation_report(
        model_comparison=model_comparison,
        champion_name="XGBoost Quantile (Champion)",
        transit_metrics=tr_metrics,
        ontime_metrics=ot_metrics,
        conformal_metrics=conf_metrics,
        route_metrics=route_metrics,
        vessel_class_metrics=vclass_metrics,
        dataset_summary=dataset_summary
    )
    
    # Save evaluation metrics json for API
    eval_json_path = "artifacts/model_registry/evaluation_metrics.json"
    with open(eval_json_path, "w") as f:
        json.dump({
            "freight_champion": "xgboost_quantile_v1",
            "metrics": xgb_m,
            "all_models": {m["model"]: m for m in model_comparison},
            "transit_metrics": tr_metrics,
            "ontime_metrics": ot_metrics,
            "conformal_coverage": conf_metrics,
            "route_metrics": route_metrics,
            "vessel_class_metrics": vclass_metrics
        }, f, indent=2)
        
    logging.info(f"Evaluation complete. Report and metrics saved to {eval_json_path}")


if __name__ == "__main__":
    run_full_evaluation()
