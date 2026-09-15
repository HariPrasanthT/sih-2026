import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))
"""
Script 06: Create strict chronological train/validation/test splits.
- Train: 2020-2024 (5 years)
- Validation: 2025 (1 year)
- Test: 2026 (1 year out-of-time test)
Generates: reports/time_split_visualization.png
"""
import logging
import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

# pyrefly: ignore [missing-import]
from src.data.loaders import load_master_dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def create_chronological_splits(
    df: pd.DataFrame,
    output_dir: str = "data/splits",
    time_col: str = "forecast_date"
):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    df_sorted = df.sort_values(time_col).reset_index(drop=True)
    dt_series = pd.to_datetime(df_sorted[time_col])
    
    train_mask = (dt_series.dt.year >= 2020) & (dt_series.dt.year <= 2024)
    val_mask = (dt_series.dt.year == 2025)
    test_mask = (dt_series.dt.year >= 2026)
    
    train_df = df_sorted[train_mask].copy()
    val_df = df_sorted[val_mask].copy()
    test_df = df_sorted[test_mask].copy()
    
    train_path = os.path.join(output_dir, "train.parquet")
    val_path = os.path.join(output_dir, "validation.parquet")
    test_path = os.path.join(output_dir, "test.parquet")
    
    train_df.to_parquet(train_path, index=False)
    val_df.to_parquet(val_path, index=False)
    test_df.to_parquet(test_path, index=False)
    
    logging.info(
        f"Chronological Splits Created:\n"
        f"  - Train (2020-2024): {len(train_df):,} rows [{train_df[time_col].min()} to {train_df[time_col].max()}]\n"
        f"  - Val   (2025):      {len(val_df):,} rows [{val_df[time_col].min()} to {val_df[time_col].max()}]\n"
        f"  - Test  (2026):      {len(test_df):,} rows [{test_df[time_col].min()} to {test_df[time_col].max()}]"
    )

    # Generate TimeSeriesSplit Visualization
    vis_path = "reports/time_split_visualization.png"
    if os.path.exists(vis_path):
        logging.info(f"TimeSeriesSplit visualization already exists at {vis_path}. Skipping plot regeneration.")
    else:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), gridspec_kw={"height_ratios": [1, 2]})
            
            # 1. Overall Train/Val/Test Timeline
            ax1.barh(["Split Horizon"], [len(train_df)], color="#1f77b4", label="Train (2020–2024)")
            ax1.barh(["Split Horizon"], [len(val_df)], left=[len(train_df)], color="#ff7f0e", label="Validation (2025)")
            ax1.barh(["Split Horizon"], [len(test_df)], left=[len(train_df) + len(val_df)], color="#2ca02c", label="Held-Out Test (2026)")
            ax1.set_title("Master Chronological Data Split (2020–2026)", fontsize=12, fontweight="bold")
            ax1.set_xlabel("Cumulative Observation Count", fontsize=10)
            ax1.legend(loc="upper left")
            
            # 2. TimeSeriesSplit (5-fold expanding window on Train)
            tscv = TimeSeriesSplit(n_splits=5)
            train_indices = np.arange(len(train_df))
            for fold, (trn_idx, val_idx) in enumerate(tscv.split(train_indices)):
                ax2.barh([f"Fold {fold + 1}"], [len(trn_idx)], color="#38bdf8", alpha=0.85, label="Train Fold" if fold == 0 else "")
                ax2.barh([f"Fold {fold + 1}"], [len(val_idx)], left=[len(trn_idx)], color="#f59e0b", alpha=0.85, label="Val Fold" if fold == 0 else "")
                
            ax2.set_title("5-Fold Expanding Window TimeSeriesSplit (Cross-Validation)", fontsize=12, fontweight="bold")
            ax2.set_xlabel("Observations in Training Set", fontsize=10)
            ax2.legend(loc="upper left")
            
            fig.tight_layout()
            fig.savefig(vis_path, dpi=150)
            plt.close(fig)
            logging.info(f"Saved TimeSeriesSplit visualization to {vis_path}")
        except Exception as e:
            logging.error(f"Error creating time split plot: {e}")
        
    return train_df, val_df, test_df


if __name__ == "__main__":
    logging.info("STEP 6: Creating Chronological Splits...")
    df_master = load_master_dataset()
    if df_master is None:
        # pyrefly: ignore [missing-import]
        from src.features.feature_pipeline import generate_development_dataset
        df_master = generate_development_dataset()
        
    create_chronological_splits(df_master)
