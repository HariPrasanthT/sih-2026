import os
import sys
import json
import logging
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler, MinMaxScaler, RobustScaler
from sklearn.compose import ColumnTransformer

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))

# pyrefly: ignore [missing-import]
from src.data.loaders import load_training_splits
# pyrefly: ignore [missing-import]
from src.models.freight.xgboost_quantile import XGBoostQuantileFreightModel
# pyrefly: ignore [missing-import]
from src.explainability.shap_explainer import FreightSHAPExplainer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BUILD_ARTIFACTS")


def build_pipeline_artifacts():
    logger.info("=== STEP 15: Building & Serializing Encoders, Scalers, Preprocessors & SHAP Artifacts ===")
    
    train_df, val_df, test_df = load_training_splits()
    if train_df is None:
        raise FileNotFoundError("Training split data not found. Run previous pipeline steps first.")
    
    df_clean = train_df.bfill().ffill()

    # --------------------------------------------------------------------------
    # 1. Encoders: artifacts/encoders/
    # --------------------------------------------------------------------------
    os.makedirs("artifacts/encoders", exist_ok=True)
    cat_cols = ["origin_port", "destination_port", "cargo_type", "vessel_class"]
    mappings = {}

    for col in cat_cols:
        if col in df_clean.columns:
            le = LabelEncoder()
            le.fit(df_clean[col].astype(str))
            joblib.dump(le, f"artifacts/encoders/{col}_encoder.joblib")
            mappings[col] = {label: int(idx) for idx, label in enumerate(le.classes_)}
            logger.info(f"Saved {col}_encoder.joblib ({len(le.classes_)} classes)")

    # Multi-column OneHotEncoder
    ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    available_cats = [c for c in cat_cols if c in df_clean.columns]
    ohe.fit(df_clean[available_cats])
    joblib.dump(ohe, "artifacts/encoders/one_hot_encoder.joblib")
    
    with open("artifacts/encoders/categorical_mappings.json", "w") as f:
        json.dump(mappings, f, indent=2)
    logger.info("Saved categorical_mappings.json and one_hot_encoder.joblib")

    # --------------------------------------------------------------------------
    # 2. Scalers: artifacts/scalers/
    # --------------------------------------------------------------------------
    os.makedirs("artifacts/scalers", exist_ok=True)
    candidate_numeric = [
        "distance_nm",
        "bdi_index",
        "bunker_vlsfo_usd_ton",
        "usd_inr_rate",
        "freight_lag_1d",
        "freight_lag_7d",
        "freight_lag_30d",
        "freight_rolling_mean_7d",
        "freight_rolling_mean_30d",
        "freight_rolling_mean_90d",
        "freight_rolling_std_7d",
        "freight_rolling_std_30d",
        "freight_momentum_7d",
        "freight_volatility_30d",
        "derived_congestion_index",
    ]
    numeric_cols = [c for c in candidate_numeric if c in df_clean.columns]

    X_num = df_clean[numeric_cols].fillna(0.0)

    # Standard Scaler (Z-Score)
    std_scaler = StandardScaler()
    std_scaler.fit(X_num)
    joblib.dump(std_scaler, "artifacts/scalers/standard_scaler.joblib")

    # MinMax Scaler [0, 1]
    mm_scaler = MinMaxScaler()
    mm_scaler.fit(X_num)
    joblib.dump(mm_scaler, "artifacts/scalers/minmax_scaler.joblib")

    # Robust Scaler (IQR based)
    rob_scaler = RobustScaler()
    rob_scaler.fit(X_num)
    joblib.dump(rob_scaler, "artifacts/scalers/robust_scaler.joblib")

    scaler_meta = {
        "numeric_features": numeric_cols,
        "n_samples": len(X_num),
        "feature_means": {col: round(float(m), 4) for col, m in zip(numeric_cols, std_scaler.mean_)},
        "feature_scales": {col: round(float(s), 4) for col, s in zip(numeric_cols, std_scaler.scale_)}
    }
    with open("artifacts/scalers/scaler_feature_names.json", "w") as f:
        json.dump(scaler_meta, f, indent=2)
    logger.info(f"Saved standard, minmax, robust scalers across {len(numeric_cols)} numeric features")

    # --------------------------------------------------------------------------
    # 3. Preprocessors: artifacts/preprocessors/
    # --------------------------------------------------------------------------
    os.makedirs("artifacts/preprocessors", exist_ok=True)
    column_transformer = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), available_cats)
        ],
        remainder="drop"
    )
    column_transformer.fit(df_clean)
    joblib.dump(column_transformer, "artifacts/preprocessors/feature_preprocessor.joblib")

    preprocessor_config = {
        "pipeline_name": "MaritimeFreightFeaturePreprocessor",
        "numeric_transformers": ["StandardScaler"],
        "numeric_columns": numeric_cols,
        "categorical_transformers": ["OneHotEncoder"],
        "categorical_columns": available_cats,
        "total_transformed_features": int(column_transformer.transform(df_clean.head(5)).shape[1])
    }
    with open("artifacts/preprocessors/preprocessor_config.json", "w") as f:
        json.dump(preprocessor_config, f, indent=2)
    logger.info("Saved feature_preprocessor.joblib and preprocessor_config.json")

    # --------------------------------------------------------------------------
    # 4. Ensemble Artifacts: artifacts/models/ensemble/
    # --------------------------------------------------------------------------
    os.makedirs("artifacts/models/ensemble", exist_ok=True)
    freight_ens_path = "artifacts/models/freight/ensemble_freight.joblib"
    if os.path.exists(freight_ens_path):
        import shutil
        shutil.copyfile(freight_ens_path, "artifacts/models/ensemble/ensemble_freight.joblib")
        logger.info("Synced ensemble model to artifacts/models/ensemble/ensemble_freight.joblib")

    ensemble_meta = {
        "model_name": "QuantileEnsembleFreightModel",
        "description": "Validation-loss optimized combination of XGBoost and LightGBM quantile regressors",
        "quantiles": [0.10, 0.50, 0.90],
        "primary_metric": "pinball_loss",
        "artifact_file": "ensemble_freight.joblib"
    }
    with open("artifacts/models/ensemble/ensemble_metadata.json", "w") as f:
        json.dump(ensemble_meta, f, indent=2)
    logger.info("Saved ensemble_metadata.json")

    # --------------------------------------------------------------------------
    # 5. SHAP Artifacts: artifacts/shap/
    # --------------------------------------------------------------------------
    os.makedirs("artifacts/shap", exist_ok=True)
    xgb_model_path = "artifacts/models/freight/xgboost_freight"
    if os.path.exists(f"{xgb_model_path}_meta.joblib"):
        xgb_model = XGBoostQuantileFreightModel.load(xgb_model_path)
        explainer = FreightSHAPExplainer(xgb_model, xgb_model.feature_names)
        joblib.dump(explainer, "artifacts/shap/shap_explainer.joblib")

        importances = explainer.get_global_importance(top_k=15)
        with open("artifacts/shap/feature_importance.json", "w") as f:
            json.dump(importances, f, indent=2)

        shap_summary = {
            "model_evaluated": "XGBoostQuantileFreightModel_P50",
            "feature_count": len(xgb_model.feature_names),
            "top_drivers": importances[:5],
            "feature_attributions": importances
        }
        with open("artifacts/shap/shap_summary_values.json", "w") as f:
            json.dump(shap_summary, f, indent=2)

        shap_metadata = {
            "explainer_type": "TreeExplainer_SHAP",
            "target": "freight_usd_per_ton",
            "quantiles_explained": [0.10, 0.50, 0.90],
            "top_feature": importances[0]["feature"] if importances else "distance_nm"
        }
        with open("artifacts/shap/shap_metadata.json", "w") as f:
            json.dump(shap_metadata, f, indent=2)
        logger.info("Saved SHAP explainer, feature importance, and summary artifacts")

    logger.info("=== All Pipeline Artifacts Built Successfully! ===")


if __name__ == "__main__":
    build_pipeline_artifacts()
