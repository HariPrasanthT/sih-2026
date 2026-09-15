"""
Baseline Reference Models for Freight Forecasting Benchmark.
"""
# pyrefly: ignore [missing-import]
from src.models.baselines.naive import (
    NaiveLastValueModel,
    MovingAverageModel,
    SeasonalNaiveModel,
)

__all__ = [
    "NaiveLastValueModel",
    "MovingAverageModel",
    "SeasonalNaiveModel",
]
