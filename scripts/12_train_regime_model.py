import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))
"""
Script 12: Train Hidden Markov Model for Freight Market Regimes.
"""
import logging
import pandas as pd
import numpy as np
# pyrefly: ignore [missing-import]
from src.data.loaders import load_training_splits
# pyrefly: ignore [missing-import]
from src.models.regime.hmm_model import MarketRegimeHMM

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if __name__ == "__main__":
    logging.info("STEP 12: Training Market Regime HMM...")
    train_df, val_df, test_df = load_training_splits()
    
    train_clean = train_df.bfill().ffill()
    
    returns = train_clean.get("freight_pct_change_7d", pd.Series(0, index=train_clean.index)).values
    volatility = train_clean.get("freight_volatility_30d", pd.Series(0.04, index=train_clean.index)).values
    
    X_regime = np.column_stack([returns, volatility])
    
    hmm_model = MarketRegimeHMM(n_states=3)
    hmm_model.fit(X_regime)
    
    os.makedirs("artifacts/models/regime", exist_ok=True)
    hmm_model.save("artifacts/models/regime/hmm_regime.joblib")
    logging.info("Market Regime HMM model saved.")
