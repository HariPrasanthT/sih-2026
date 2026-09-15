"""
Unit tests for data validation, unit normalization, and deduplication.
"""
import pytest
import pandas as pd
# pyrefly: ignore [missing-import]
from src.data.validation import validate_dataframe_schema, validate_vessel_records
# pyrefly: ignore [missing-import]
from src.data.normalization import normalize_freight_rate, normalize_draft_meters, normalize_speed_knots
# pyrefly: ignore [missing-import]
from src.data.deduplication import deduplicate_dataset


def test_validate_dataframe_schema():
    df = pd.DataFrame({
        "port": ["PARADIP", "DHAMRA"],
        "rate": [18.5, 22.0]
    })
    is_valid, issues = validate_dataframe_schema(df, required_cols=["port", "rate"], numeric_ranges={"rate": (5.0, 50.0)})
    assert is_valid is True
    assert len(issues) == 0

    # Invalid case
    is_valid_bad, issues_bad = validate_dataframe_schema(df, required_cols=["port", "missing_col"])
    assert is_valid_bad is False
    assert len(issues_bad) > 0


def test_unit_normalization():
    assert normalize_freight_rate(24.5, "USD_PER_TON") == 24.5
    assert normalize_freight_rate(-5.0, "USD_PER_TON") is None
    assert normalize_freight_rate(1500, "USD/TEU") is None  # Incompatible TEU rejected
    assert normalize_draft_meters(14.2) == 14.2
    assert normalize_draft_meters(35.0) is None  # Impossible draft
    assert normalize_speed_knots(14.5) == 14.5
    assert normalize_speed_knots(45.0) is None  # Impossible cargo vessel speed


def test_deduplication():
    df = pd.DataFrame({
        "id": [1, 2, 2, 3],
        "date": ["2026-01-01", "2026-01-02", "2026-01-02", "2026-01-03"],
        "val": [10, 20, 20, 30]
    })
    df_clean, audit = deduplicate_dataset(df, subset_cols=["id", "date"])
    assert len(df_clean) == 3
    assert audit["duplicates_removed"] == 1
