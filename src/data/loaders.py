"""
Unified Data Loaders.
Provides convenient access to processed tables, splits, port metadata, and candidate fleet.
"""
import os
import logging
from typing import Optional, Tuple
import pandas as pd

logger = logging.getLogger(__name__)


def load_port_master(path: str = "data/processed/ports/port_master.parquet") -> pd.DataFrame:
    """Load canonical port master table."""
    if os.path.exists(path):
        return pd.read_parquet(path)
    # pyrefly: ignore [missing-import]
    from src.data.port_mapping import export_port_master_tables
    export_port_master_tables()
    return pd.read_parquet(path)


def load_vessel_master(path: str = "data/processed/vessel/vessel_master.parquet") -> pd.DataFrame:
    """Load vessel fleet master table."""
    if os.path.exists(path):
        return pd.read_parquet(path)
    # pyrefly: ignore [missing-import]
    from src.data.vessel_mapping import export_vessel_master_table
    export_vessel_master_table()
    return pd.read_parquet(path)


def load_port_congestion(path: str = "data/processed/ports/port_congestion.parquet") -> Optional[pd.DataFrame]:
    """Load derived port congestion and daily activity table."""
    if os.path.exists(path):
        return pd.read_parquet(path)
    return None


def load_training_splits(splits_dir: str = "data/splits") -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """Load train, validation, and test parquet splits."""
    train_path = os.path.join(splits_dir, "train.parquet")
    val_path = os.path.join(splits_dir, "validation.parquet")
    test_path = os.path.join(splits_dir, "test.parquet")
    
    train_df = pd.read_parquet(train_path) if os.path.exists(train_path) else None
    val_df = pd.read_parquet(val_path) if os.path.exists(val_path) else None
    test_df = pd.read_parquet(test_path) if os.path.exists(test_path) else None
    
    return train_df, val_df, test_df


def load_master_dataset(path: str = "data/processed/master/training_master.parquet") -> Optional[pd.DataFrame]:
    """Load training master table."""
    if os.path.exists(path):
        return pd.read_parquet(path)
    return None
