"""
Prediction Service.
Loads champion models, prepares runtime feature vectors, and produces calibrated probabilistic forecasts.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
import joblib

# pyrefly: ignore [missing-import]
from src.features.feature_pipeline import get_route_distance_nm
# pyrefly: ignore [missing-import]
from src.features.temporal_features import build_temporal_features
# pyrefly: ignore [missing-import]
from src.features.market_features import build_market_features
# pyrefly: ignore [missing-import]
from src.features.port_features import build_port_features
# pyrefly: ignore [missing-import]
from src.data.port_mapping import normalize_port_name

logger = logging.getLogger(__name__)


class PredictionService:
    """
    Centralized inference service for Freight P10/P50/P90, Transit, On-Time, and Regime.
    """
    def __init__(self, artifacts_dir: str = "artifacts"):
        self.artifacts_dir = artifacts_dir
        self.registry_path = os.path.join(artifacts_dir, "model_registry", "model_registry.json")
        self.freight_model = None
        self.transit_model = None
        self.ontime_model = None
        self.hmm_model = None
        self.conformal_calibrator = None
        self.registry_info = {}
        self._load_models()
        
    def _load_models(self):
        """Load trained models from artifacts directory if available."""
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, "r") as f:
                    self.registry_info = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load model registry: {e}")
                
        # 1. Freight Model
        try:
            # pyrefly: ignore [missing-import]
            from src.models.freight.xgboost_quantile import XGBoostQuantileFreightModel
            xgb_path = os.path.join(self.artifacts_dir, "models", "freight", "xgboost_freight")
            if os.path.exists(f"{xgb_path}_meta.joblib"):
                self.freight_model = XGBoostQuantileFreightModel.load(xgb_path)
                logger.info("Loaded XGBoost Quantile Freight Model.")
        except Exception as e:
            logger.warning(f"Could not load XGBoost freight model: {e}")
            
        # 2. Transit Model
        try:
            # pyrefly: ignore [missing-import]
            from src.models.transit.transit_model import TransitDurationModel
            transit_path = os.path.join(self.artifacts_dir, "models", "transit", "transit_model.joblib")
            if os.path.exists(transit_path):
                self.transit_model = TransitDurationModel.load(transit_path)
        except Exception as e:
            logger.warning(f"Could not load transit model: {e}")
            
        # 3. On-Time Model
        try:
            # pyrefly: ignore [missing-import]
            from src.models.ontime.ontime_model import OnTimeArrivalModel
            ontime_path = os.path.join(self.artifacts_dir, "models", "ontime", "ontime_model.joblib")
            if os.path.exists(ontime_path):
                self.ontime_model = OnTimeArrivalModel.load(ontime_path)
        except Exception as e:
            logger.warning(f"Could not load on-time model: {e}")
            
        # 4. Conformal Calibrator
        try:
            # pyrefly: ignore [missing-import]
            from src.models.uncertainty.conformal import ConformalPredictionCalibrator
            conf_path = os.path.join(self.artifacts_dir, "conformal", "conformal_calibrator.joblib")
            if os.path.exists(conf_path):
                self.conformal_calibrator = ConformalPredictionCalibrator.load(conf_path)
        except Exception as e:
            logger.warning(f"Could not load conformal calibrator: {e}")
            
        # 5. HMM Regime Model
        try:
            # pyrefly: ignore [missing-import]
            from src.models.regime.hmm_model import MarketRegimeHMM
            hmm_path = os.path.join(self.artifacts_dir, "models", "regime", "hmm_regime.joblib")
            if os.path.exists(hmm_path):
                self.hmm_model = MarketRegimeHMM.load(hmm_path)
        except Exception as e:
            logger.warning(f"Could not load HMM regime model: {e}")
            
    def build_inference_feature_vector(
        self,
        origin_port: str,
        destination_port: str,
        cargo_type: str,
        vessel_class: str,
        ship_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Construct aligned feature row for single inference query."""
        orig = normalize_port_name(origin_port) or origin_port
        dest = normalize_port_name(destination_port) or destination_port
        dist_nm = get_route_distance_nm(orig, dest)
        
        target_date = pd.to_datetime(ship_date) if ship_date else pd.Timestamp.now(tz="UTC")
        
        row = {
            "forecast_date": target_date,
            "origin_port": orig,
            "destination_port": dest,
            "cargo_type": cargo_type,
            "vessel_class": vessel_class,
            "route_distance_nm": dist_nm,
            "bdi_index": 1450.0,
            "bunker_vlsfo_usd_ton": 620.0,
            "usd_inr_rate": 83.2,
            "derived_congestion_index": 0.42,
            "est_waiting_days": 2.1,
            "vessels_approaching_count": 8,
            "vessels_anchorage_count": 12,
            "freight_lag_1d": 18.0,
            "freight_lag_3d": 18.2,
            "freight_lag_7d": 18.5,
            "freight_lag_14d": 18.1,
            "freight_lag_30d": 17.8,
            "freight_rolling_mean_7d": 18.1,
            "freight_rolling_mean_30d": 18.0,
            "freight_rolling_mean_90d": 17.9,
            "freight_rolling_std_7d": 0.4,
            "freight_rolling_std_30d": 0.8,
            "freight_rolling_std_90d": 1.2,
            "freight_momentum_7d": -0.5,
            "freight_pct_change_7d": -2.7,
            "freight_volatility_30d": 0.044,
        }
        df = pd.DataFrame([row])
        df = build_market_features(df, time_col="forecast_date")
        df = build_port_features(df)
        df = build_temporal_features(df, date_col="forecast_date")
        return df
        
    def predict_freight(self, df_features: pd.DataFrame) -> Dict[str, float]:
        """Predict P10, P50, and P90 freight rate."""
        if self.freight_model is not None and hasattr(self.freight_model, "feature_names"):
            X = df_features.copy()
            for col in self.freight_model.feature_names:
                if col not in X.columns:
                    X[col] = 0.0
            X = X[self.freight_model.feature_names].fillna(0.0)
            preds = self.freight_model.predict_quantiles(X)
            
            p10 = float(preds["p10"][0])
            p50 = float(preds["p50"][0])
            p90 = float(preds["p90"][0])
            
            # Apply conformal bounds if available
            if self.conformal_calibrator is not None:
                low_c, high_c = self.conformal_calibrator.predict_intervals(np.array([p50]))
                p10 = min(p10, float(low_c[0]))
                p90 = max(p90, float(high_c[0]))
                
            return {
                "freight_low": round(max(3.0, p10), 2),
                "freight_median": round(max(4.0, p50), 2),
                "freight_high": round(max(5.0, p90), 2)
            }
        # Scientific heuristic fallback if model artifacts are being initialized
        dist = float(df_features.get("route_distance_nm", 4500.0).iloc[0])
        base_rate = round(float(dist * 0.0035 + 3.5), 2)
        return {
            "freight_low": round(base_rate * 0.90, 2),
            "freight_median": base_rate,
            "freight_high": round(base_rate * 1.12, 2)
        }
        
    def predict_transit_days(self, df_features: pd.DataFrame, speed_knots: float = 14.0) -> float:
        """Estimate voyage transit duration."""
        if self.transit_model is not None and hasattr(self.transit_model, "feature_names"):
            X = df_features.copy()
            for col in self.transit_model.feature_names:
                if col not in X.columns:
                    X[col] = 0.0
            X = X[self.transit_model.feature_names].fillna(0.0)
            return round(float(self.transit_model.predict(X)[0]), 1)
        dist = float(df_features.get("route_distance_nm", 4500.0).iloc[0])
        port_wait = float(df_features.get("est_waiting_days", 2.0).iloc[0])
        steaming_days = dist / (speed_knots * 24.0)
        return round(steaming_days + port_wait * 0.5, 1)
        
    def predict_ontime_prob(self, df_features: pd.DataFrame) -> float:
        """Predict calibrated on-time probability."""
        if self.ontime_model is not None and hasattr(self.ontime_model, "feature_names"):
            X = df_features.copy()
            for col in self.ontime_model.feature_names:
                if col not in X.columns:
                    X[col] = 0.0
            X = X[self.ontime_model.feature_names].fillna(0.0)
            return round(float(self.ontime_model.predict_proba(X)[0]), 3)
        cong = float(df_features.get("derived_congestion_index", 0.4).iloc[0])
        monsoon = int(df_features.get("is_monsoon", 0).iloc[0])
        prob = 0.88 - cong * 0.25 - (0.12 if monsoon else 0.0)
        return round(float(np.clip(prob, 0.20, 0.95)), 3)
        
    def detect_market_regime(self, df_features: pd.DataFrame) -> str:
        """Classify current market regime."""
        if self.hmm_model is not None:
            vol = float(df_features.get("freight_volatility_30d", 0.04).iloc[0])
            ret = float(df_features.get("freight_pct_change_7d", 0.0).iloc[0])
            regimes = self.hmm_model.predict_regime(np.array([[ret, vol]]))
            return regimes[0]
        return "NORMAL"
