"""
Unit tests for multi-objective vessel charter optimizer and Pareto ranking.
"""
import pytest
import pandas as pd
# pyrefly: ignore [missing-import]
from src.optimization.optimizer import VesselCharterOptimizer


@pytest.fixture
def candidate_fleet():
    return pd.DataFrame([
        {
            "vessel_id": "V_CHEAP",
            "vessel_name": "Economy Bulk",
            "predicted_cost_median": 800000.0,
            "estimated_transit_days": 18.0,
            "probability_on_time": 0.70,
            "port_feasible": True,
            "availability_status": "available",
            "vessel_class": "Capesize"
        },
        {
            "vessel_id": "V_FAST",
            "vessel_name": "Speed Star",
            "predicted_cost_median": 1200000.0,
            "estimated_transit_days": 10.0,
            "probability_on_time": 0.75,
            "port_feasible": True,
            "availability_status": "available",
            "vessel_class": "Capesize"
        },
        {
            "vessel_id": "V_RELIABLE",
            "vessel_name": "Punctual Carrier",
            "predicted_cost_median": 1100000.0,
            "estimated_transit_days": 15.0,
            "probability_on_time": 0.98,
            "port_feasible": True,
            "availability_status": "available",
            "vessel_class": "Capesize"
        },
        {
            "vessel_id": "V_INFEASIBLE",
            "vessel_name": "Ineligible Carrier",
            "predicted_cost_median": 500000.0,
            "estimated_transit_days": 8.0,
            "probability_on_time": 0.99,
            "port_feasible": False,
            "availability_status": "available",
            "vessel_class": "Capesize"
        }
    ])


def test_weight_validation():
    with pytest.raises(ValueError):
        VesselCharterOptimizer.validate_weights(0.5, 0.5, 0.5)  # Sums to 1.5

    with pytest.raises(ValueError):
        VesselCharterOptimizer.validate_weights(-0.1, 0.6, 0.5)  # Negative weight


def test_cost_dominant_ranking(candidate_fleet):
    optimizer = VesselCharterOptimizer()
    ranked = optimizer.optimize(candidate_fleet, weight_cost=1.0, weight_speed=0.0, weight_reliability=0.0)
    assert ranked.iloc[0]["vessel_id"] == "V_CHEAP"
    assert "V_INFEASIBLE" not in ranked["vessel_id"].values


def test_speed_dominant_ranking(candidate_fleet):
    optimizer = VesselCharterOptimizer()
    ranked = optimizer.optimize(candidate_fleet, weight_cost=0.0, weight_speed=1.0, weight_reliability=0.0)
    assert ranked.iloc[0]["vessel_id"] == "V_FAST"
    assert "V_INFEASIBLE" not in ranked["vessel_id"].values


def test_reliability_dominant_ranking(candidate_fleet):
    optimizer = VesselCharterOptimizer()
    ranked = optimizer.optimize(candidate_fleet, weight_cost=0.0, weight_speed=0.0, weight_reliability=1.0)
    assert ranked.iloc[0]["vessel_id"] == "V_RELIABLE"
    assert "V_INFEASIBLE" not in ranked["vessel_id"].values


def test_pareto_frontier(candidate_fleet):
    optimizer = VesselCharterOptimizer()
    feasible = candidate_fleet[candidate_fleet["port_feasible"]].copy()
    pareto = optimizer.compute_pareto_frontier(feasible)
    # V_CHEAP, V_FAST, and V_RELIABLE each excel in one distinct objective, so all 3 are Pareto-optimal
    assert len(pareto) == 3
    assert set(pareto["vessel_id"]) == {"V_CHEAP", "V_FAST", "V_RELIABLE"}


def test_what_if_sensitivity(candidate_fleet):
    optimizer = VesselCharterOptimizer()
    sens = optimizer.what_if_sensitivity(candidate_fleet)
    assert "Cost-Focused" in sens
    assert "Speed-Express" in sens
    assert "Reliability-Priority" in sens
    assert sens["Cost-Focused"].iloc[0]["vessel_id"] == "V_CHEAP"
    assert sens["Speed-Express"].iloc[0]["vessel_id"] == "V_FAST"
