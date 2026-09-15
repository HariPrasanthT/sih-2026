"""
Data Validation Engine.
Performs strict schema and range validation checks, identifying anomalies and domain violations.
"""
import logging
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def validate_dataframe_schema(
    df: pd.DataFrame,
    required_cols: List[str],
    numeric_ranges: Dict[str, Tuple[float, float]] = None
) -> Tuple[bool, List[str]]:
    """
    Validate that required columns exist and numerical values satisfy physical bounds.
    """
    issues = []
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        issues.append(f"Missing required columns: {missing_cols}")
        
    if numeric_ranges:
        for col, (min_val, max_val) in numeric_ranges.items():
            if col in df.columns:
                series = pd.to_numeric(df[col], errors="coerce")
                out_of_bounds = series[(series < min_val) | (series > max_val)].dropna()
                if not out_of_bounds.empty:
                    issues.append(f"Column '{col}' has {len(out_of_bounds)} values outside valid range [{min_val}, {max_val}]")
                    
    is_valid = len(issues) == 0
    return is_valid, issues


def validate_vessel_records(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Validate vessel dataset against maritime physical constraints.
    """
    audit = {"initial_rows": len(df), "rejected_reasons": {}}
    valid_mask = pd.Series(True, index=df.index)
    
    # 1. Draft range [4.0m, 25.0m]
    if "draft_m" in df.columns:
        invalid_draft = (df["draft_m"] < 4.0) | (df["draft_m"] > 25.0)
        if invalid_draft.any():
            audit["rejected_reasons"]["invalid_draft"] = int(invalid_draft.sum())
            valid_mask &= ~invalid_draft
            
    # 2. LOA range [50.0m, 400.0m]
    if "loa_m" in df.columns:
        invalid_loa = (df["loa_m"] < 50.0) | (df["loa_m"] > 400.0)
        if invalid_loa.any():
            audit["rejected_reasons"]["invalid_loa"] = int(invalid_loa.sum())
            valid_mask &= ~invalid_loa
            
    # 3. Beam range [10.0m, 65.0m]
    if "beam_m" in df.columns:
        invalid_beam = (df["beam_m"] < 10.0) | (df["beam_m"] > 65.0)
        if invalid_beam.any():
            audit["rejected_reasons"]["invalid_beam"] = int(invalid_beam.sum())
            valid_mask &= ~invalid_beam
            
    # 4. DWT positive
    if "dwt" in df.columns:
        invalid_dwt = (df["dwt"] < 5000) | (df["dwt"] > 450000)
        if invalid_dwt.any():
            audit["rejected_reasons"]["invalid_dwt"] = int(invalid_dwt.sum())
            valid_mask &= ~invalid_dwt
            
    df_clean = df[valid_mask].copy()
    audit["final_rows"] = len(df_clean)
    audit["dropped_rows"] = audit["initial_rows"] - audit["final_rows"]
    
    return df_clean, audit
