"""
Data Deduplication Engine.
Removes duplicate timestamps, vessel IDs, and observations with audit tracking.
"""
import logging
from typing import List, Tuple, Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)


def deduplicate_dataset(
    df: pd.DataFrame,
    subset_cols: List[str],
    keep: str = "first"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Deduplicate dataframe based on subset of columns, recording count and percentage.
    """
    initial_len = len(df)
    existing_cols = [c for c in subset_cols if c in df.columns]
    
    if not existing_cols:
        return df, {"initial_count": initial_len, "duplicates_removed": 0, "pct_removed": 0.0}
        
    df_clean = df.drop_duplicates(subset=existing_cols, keep=keep).copy()
    removed = initial_len - len(df_clean)
    pct = round((removed / initial_len * 100.0) if initial_len > 0 else 0.0, 2)
    
    audit = {
        "initial_count": initial_len,
        "final_count": len(df_clean),
        "duplicates_removed": removed,
        "pct_removed": pct,
        "keys": existing_cols
    }
    
    if removed > 0:
        logger.info(f"Deduplication removed {removed} rows ({pct}%) using keys {existing_cols}")
        
    return df_clean, audit
