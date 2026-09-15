"""
Multi-Objective Vessel Ranking and Optimization Engine.
Balances Total Voyage Cost, Transit Speed, and Schedule Reliability with configurable weights.
"""
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def rank_vessels(
    candidates_df: pd.DataFrame,
    weight_cost: float = 0.50,
    weight_speed: float = 0.30,
    weight_reliability: float = 0.20,
    top_n: int = 5
) -> pd.DataFrame:
    """
    Compute multi-objective score and rank candidate vessels.
    Weights are normalized to sum to 1.0.
    """
    if candidates_df.empty:
        return candidates_df
        
    df = candidates_df.copy()
    
    # Infeasible vessels must never appear in ranked recommendations
    if "port_feasible" in df.columns:
        df = df[df["port_feasible"] == True].copy()
        if df.empty:
            return df
    
    # Normalize weights
    total_w = weight_cost + weight_speed + weight_reliability
    if total_w <= 0:
        w_cost, w_speed, w_rel = 0.50, 0.30, 0.20
    else:
        w_cost = weight_cost / total_w
        w_speed = weight_speed / total_w
        w_rel = weight_reliability / total_w
        
    # Extract series
    cost = df["predicted_cost_median"].values
    transit = df["estimated_transit_days"].values
    reliability = df["probability_on_time"].values
    
    # Min-Max Normalization within the feasible candidate set
    min_c, max_c = np.min(cost), np.max(cost)
    norm_cost = (cost - min_c) / (max_c - min_c + 1e-6) if max_c > min_c else np.zeros_like(cost)
    
    min_t, max_t = np.min(transit), np.max(transit)
    norm_transit = (transit - min_t) / (max_t - min_t + 1e-6) if max_t > min_t else np.zeros_like(transit)
    
    # Multi-Objective Score: higher is better
    # Cost component: lower cost is better -> (1 - norm_cost)
    # Transit component: shorter transit is better -> (1 - norm_transit)
    # Reliability component: higher probability is better -> reliability
    score = w_cost * (1.0 - norm_cost) + w_speed * (1.0 - norm_transit) + w_rel * reliability
    df["multi_objective_score"] = np.round(score, 4)
    
    # Sort descending by score
    df = df.sort_values("multi_objective_score", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    
    # Filter top_n (bounded between 3 and 5)
    n_clamped = max(3, min(top_n, 5, len(df)))
    return df.head(n_clamped)
