import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))
"""
Script 07: Benchmark baseline models on validation split.
"""
import logging
# pyrefly: ignore [missing-import]
from src.data.loaders import load_training_splits
# pyrefly: ignore [missing-import]
from src.models.baselines.naive import NaiveLastValueModel, MovingAverageModel, SeasonalNaiveModel
# pyrefly: ignore [missing-import]
from src.evaluation.freight_metrics import evaluate_freight_predictions

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if __name__ == "__main__":
    logging.info("STEP 7: Evaluating Baseline Benchmark Models...")
    train_df, val_df, test_df = load_training_splits()
    
    y_val = val_df["freight_usd_per_ton"].values
    
    # 1. Naive
    naive = NaiveLastValueModel()
    pred_naive = naive.predict(val_df)
    m_naive = evaluate_freight_predictions(y_val, pred_naive)
    logging.info(f"Baseline Naive (Last-Value): MAE=${m_naive['mae_usd_ton']}, MAPE={m_naive['mape_pct']}%, R2={m_naive['r2_score']}")
    
    # 2. Moving Average
    ma7 = MovingAverageModel("freight_rolling_mean_7d")
    pred_ma7 = ma7.predict(val_df)
    m_ma7 = evaluate_freight_predictions(y_val, pred_ma7)
    logging.info(f"Baseline Moving Avg 7d:    MAE=${m_ma7['mae_usd_ton']}, MAPE={m_ma7['mape_pct']}%, R2={m_ma7['r2_score']}")
    
    # 3. Seasonal Naive
    snaive = SeasonalNaiveModel("freight_lag_30d")
    pred_snaive = snaive.predict(val_df)
    m_snaive = evaluate_freight_predictions(y_val, pred_snaive)
    logging.info(f"Baseline Seasonal Naive 30d: MAE=${m_snaive['mae_usd_ton']}, MAPE={m_snaive['mape_pct']}%, R2={m_snaive['r2_score']}")
