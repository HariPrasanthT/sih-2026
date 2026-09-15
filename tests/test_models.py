"""
Unit tests for ML models, quantile predictions, and monotonicity.
"""
import pytest
import pandas as pd
import numpy as np
# pyrefly: ignore [missing-import]
from src.models.freight.xgboost_quantile import XGBoostQuantileFreightModel
# pyrefly: ignore [missing-import]
from src.models.freight.lightgbm_quantile import LightGBMQuantileFreightModel
# pyrefly: ignore [missing-import]
from src.models.transit.transit_model import TransitDurationModel
# pyrefly: ignore [missing-import]
from src.models.ontime.ontime_model import OnTimeArrivalModel


@pytest.fixture
def sample_training_data():
    np.random.seed(42)
    n = 200
    X = pd.DataFrame({
        "feat1": np.random.normal(10, 2, n),
        "feat2": np.random.normal(50, 10, n),
        "feat3": np.random.uniform(1, 5, n)
    })
    y_freight = 15.0 + 0.5 * X["feat1"] + 0.1 * X["feat2"] + np.random.normal(0, 1, n)
    y_transit = 10.0 + 0.2 * X["feat1"] + np.random.normal(0, 0.5, n)
    y_ontime = (y_transit < 12.0).astype(int)
    return X, y_freight, y_transit, y_ontime


def test_xgboost_quantile_monotonicity(sample_training_data):
    X, y_freight, _, _ = sample_training_data
    model = XGBoostQuantileFreightModel(n_estimators=30)
    model.fit(X, y_freight)
    
    preds = model.predict_quantiles(X.head(20))
    assert "p10" in preds and "p50" in preds and "p90" in preds
    
    # Check monotonicity: P10 <= P50 <= P90
    assert np.all(preds["p10"] <= preds["p50"])
    assert np.all(preds["p50"] <= preds["p90"])


def test_lightgbm_quantile_monotonicity(sample_training_data):
    X, y_freight, _, _ = sample_training_data
    model = LightGBMQuantileFreightModel(n_estimators=30)
    model.fit(X, y_freight)
    
    preds = model.predict_quantiles(X.head(20))
    assert np.all(preds["p10"] <= preds["p50"])
    assert np.all(preds["p50"] <= preds["p90"])


def test_transit_model(sample_training_data):
    X, _, y_transit, _ = sample_training_data
    model = TransitDurationModel(n_estimators=30)
    model.fit(X, y_transit)
    preds = model.predict(X.head(10))
    assert len(preds) == 10
    assert np.all(preds > 0)


def test_ontime_classifier(sample_training_data):
    X, _, _, y_ontime = sample_training_data
    model = OnTimeArrivalModel(n_estimators=30)
    model.fit(X, y_ontime)
    probs = model.predict_proba(X.head(10))
    assert len(probs) == 10
    assert np.all((probs >= 0.0) & (probs <= 1.0))
