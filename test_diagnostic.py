import sys, os
import functools
print = functools.partial(print, flush=True)
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
print("TEST SCRIPT: Python version:", sys.version)

try:
    print("Loading splits...")
    # pyrefly: ignore [missing-import]
    from src.data.loaders import load_training_splits
    train_df, val_df, test_df = load_training_splits()
    print(f"Loaded splits: train={len(train_df)}, val={len(val_df)}, test={len(test_df)}")

    print("Importing XGBoost...")
    # pyrefly: ignore [missing-import]
    from src.models.freight.xgboost_quantile import XGBoostQuantileFreightModel
    print("XGBoost imported.")
    print("Importing LightGBM...")
    # pyrefly: ignore [missing-import]
    from src.models.freight.lightgbm_quantile import LightGBMQuantileFreightModel
    print("LightGBM imported.")
    print("Importing CatBoost/HistGBM...")
    # pyrefly: ignore [missing-import]
    from src.models.freight.catboost_model import CatBoostFreightModel
    print("CatBoost/HistGBM imported.")
    print("Importing RandomForest...")
    # pyrefly: ignore [missing-import]
    from src.models.freight.random_forest import RandomForestFreightModel
    print("RandomForest imported.")
    print("Importing StackingEnsemble...")
    # pyrefly: ignore [missing-import]
    from src.models.freight.stacking_ensemble import StackingQuantileFreightEnsemble
    print("StackingEnsemble imported.")
    print("All models imported successfully!")
except Exception as e:
    print(f"Error encountered: {e}")
