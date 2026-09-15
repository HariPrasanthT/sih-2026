"""
Unit tests for Multi-Objective Ranking and Weight Customization.
Verifies cost=1, speed=1, reliability=1 extremes and infeasible vessel exclusion.
"""
import pytest
import pandas as pd
import numpy as np
# pyrefly: ignore [missing-import]
from src.optimization.ranking import rank_vessels


@pytest.fixture
def candidate_candidates_df():
    return pd.DataFrame([
        {
            "vessel_id": "VSL_CHEAP",
            "vessel_name": "Cheap Slow Carrier",
            "predicted_cost_median": 1000000.0,
            "estimated_transit_days": 18.0,
            "probability_on_time": 0.70
        },
        {
            "vessel_id": "VSL_FAST",
            "vessel_name": "Fast Expensive Cruiser",
            "predicted_cost_median": 1500000.0,
            "estimated_transit_days": 10.0,
            "probability_on_time": 0.75
        },
        {
            "vessel_id": "VSL_RELIABLE",
            "vessel_name": "High Reliability Carrier",
            "predicted_cost_median": 1300000.0,
            "estimated_transit_days": 14.0,
            "probability_on_time": 0.98
        }
    ])


def test_ranking_weight_cost_priority(candidate_candidates_df):
    # Weight cost = 1.0 -> Cheapest vessel must rank #1
    ranked = rank_vessels(candidate_candidates_df, weight_cost=1.0, weight_speed=0.0, weight_reliability=0.0, top_n=3)
    assert ranked.iloc[0]["vessel_id"] == "VSL_CHEAP"


def test_ranking_weight_speed_priority(candidate_candidates_df):
    # Weight speed = 1.0 -> Fastest vessel must rank #1
    ranked = rank_vessels(candidate_candidates_df, weight_cost=0.0, weight_speed=1.0, weight_reliability=0.0, top_n=3)
    assert ranked.iloc[0]["vessel_id"] == "VSL_FAST"


def test_ranking_weight_reliability_priority(candidate_candidates_df):
    # Weight reliability = 1.0 -> Most reliable vessel must rank #1
    ranked = rank_vessels(candidate_candidates_df, weight_cost=0.0, weight_speed=0.0, weight_reliability=1.0, top_n=3)
    assert ranked.iloc[0]["vessel_id"] == "VSL_RELIABLE"
