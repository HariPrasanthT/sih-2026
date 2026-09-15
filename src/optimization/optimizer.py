"""
Multi-Objective Vessel Charter Optimizer.
Balances voyage cost, transit speed, and on-time arrival reliability.
Computes normalized multi-objective scoring, Pareto-efficient frontiers, and what-if sensitivity trade-offs.
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd

# pyrefly: ignore [missing-import]
from src.optimization.vessel_filter import filter_feasible_vessels
# pyrefly: ignore [missing-import]
from src.optimization.ranking import rank_vessels

logger = logging.getLogger(__name__)


class VesselCharterOptimizer:
    """
    Configurable multi-objective optimization engine for vessel selection.
    """
    def __init__(
        self,
        default_weight_cost: float = 0.50,
        default_weight_speed: float = 0.30,
        default_weight_reliability: float = 0.20,
        top_n: int = 5
    ):
        self.validate_weights(default_weight_cost, default_weight_speed, default_weight_reliability)
        self.w_cost = default_weight_cost
        self.w_speed = default_weight_speed
        self.w_rel = default_weight_reliability
        self.top_n = min(5, max(3, top_n))

    @staticmethod
    def validate_weights(w_cost: float, w_speed: float, w_rel: float, tolerance: float = 1e-3) -> None:
        """Verify weights are non-negative and sum to 1.0."""
        if any(w < 0.0 for w in [w_cost, w_speed, w_rel]):
            raise ValueError(f"Weights must be non-negative. Got: cost={w_cost}, speed={w_speed}, rel={w_rel}")
        total = w_cost + w_speed + w_rel
        if abs(total - 1.0) > tolerance:
            raise ValueError(f"Optimization weights must sum to 1.0. Got total = {total:.4f}")

    def optimize(
        self,
        candidates_df: pd.DataFrame,
        weight_cost: Optional[float] = None,
        weight_speed: Optional[float] = None,
        weight_reliability: Optional[float] = None,
        top_n: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Rank candidate vessels using multi-objective scoring.
        """
        wc = self.w_cost if weight_cost is None else weight_cost
        ws = self.w_speed if weight_speed is None else weight_speed
        wr = self.w_rel if weight_reliability is None else weight_reliability
        n = self.top_n if top_n is None else min(5, max(3, top_n))

        self.validate_weights(wc, ws, wr)
        return rank_vessels(
            candidates_df=candidates_df,
            weight_cost=wc,
            weight_speed=ws,
            weight_reliability=wr,
            top_n=n
        )

    def compute_pareto_frontier(self, candidates_df: pd.DataFrame) -> pd.DataFrame:
        """
        Identify Pareto-optimal vessels (non-dominated in cost, transit days, and reliability).
        A vessel is dominated if another vessel has lower or equal cost, lower or equal transit time,
        and higher or equal reliability, with at least one strictly better.
        """
        if candidates_df.empty or len(candidates_df) <= 1:
            return candidates_df

        cost_col = "predicted_total_voyage_cost" if "predicted_total_voyage_cost" in candidates_df.columns else "predicted_cost_median"
        transit_col = "estimated_transit_days"
        rel_col = "probability_on_time"

        req_cols = [cost_col, transit_col, rel_col]
        if not all(c in candidates_df.columns for c in req_cols):
            return candidates_df

        pareto_indices = []
        records = candidates_df[req_cols].to_dict(orient="records")

        for i, a in enumerate(records):
            is_dominated = False
            for j, b in enumerate(records):
                if i == j:
                    continue
                # b dominates a if b is at least as good in all objectives and strictly better in at least one
                b_cost_better = b[cost_col] <= a[cost_col]
                b_transit_better = b[transit_col] <= a[transit_col]
                b_rel_better = b[rel_col] >= a[rel_col]

                b_strictly_better = (
                    b[cost_col] < a[cost_col] or
                    b[transit_col] < a[transit_col] or
                    b[rel_col] > a[rel_col]
                )

                if b_cost_better and b_transit_better and b_rel_better and b_strictly_better:
                    is_dominated = True
                    break

            if not is_dominated:
                pareto_indices.append(i)

        df_pareto = candidates_df.iloc[pareto_indices].copy()
        df_pareto["is_pareto_optimal"] = True
        return df_pareto

    def what_if_sensitivity(
        self,
        candidates_df: pd.DataFrame,
        scenarios: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Evaluate vessel rankings across strategic scenario profiles:
        - Cost-Dominant (e.g. 0.80 / 0.10 / 0.10)
        - Speed-Priority (e.g. 0.20 / 0.70 / 0.10)
        - High-Reliability (e.g. 0.20 / 0.20 / 0.60)
        - Balanced Default (0.50 / 0.30 / 0.20)
        """
        if scenarios is None:
            scenarios = [
                {"name": "Cost-Focused", "wc": 0.80, "ws": 0.10, "wr": 0.10},
                {"name": "Speed-Express", "wc": 0.20, "ws": 0.70, "wr": 0.10},
                {"name": "Reliability-Priority", "wc": 0.20, "ws": 0.20, "wr": 0.60},
                {"name": "Balanced-Charter", "wc": 0.50, "ws": 0.30, "wr": 0.20}
            ]

        results = {}
        for sc in scenarios:
            ranked = self.optimize(
                candidates_df,
                weight_cost=sc["wc"],
                weight_speed=sc["ws"],
                weight_reliability=sc["wr"]
            )
            results[sc["name"]] = ranked

        return results
