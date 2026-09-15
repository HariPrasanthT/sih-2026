"""
Charter Strategy Decision Engine and Risk Classifier.
Generates explainable strategic recommendations: CHARTER, WAIT, or AVOID with operational risk flags.
"""
import logging
from typing import Dict, Any, List, Tuple
import pandas as pd

logger = logging.getLogger(__name__)


def evaluate_charter_decision(
    vessel_row: Dict[str, Any],
    market_regime: str = "NORMAL",
    savings_threshold_pct: float = 2.0,
    on_time_threshold: float = 0.70,
    avoid_on_time_threshold: float = 0.40
) -> Tuple[str, List[str]]:
    """
    Evaluate strategic decision: CHARTER, WAIT, or AVOID.
    Returns (decision, risk_flags).
    """
    flags = []
    
    # Check feasibility
    port_feasible = vessel_row.get("port_feasible", True)
    if not port_feasible:
        flags.append("PORT_PHYSICAL_CONSTRAINT_VIOLATION")
        return "AVOID", flags
        
    on_time_prob = float(vessel_row.get("probability_on_time", 0.5))
    savings_pct = float(vessel_row.get("savings_vs_market_pct", 0.0))
    congestion_idx = float(vessel_row.get("derived_congestion_index", 0.3))
    
    # 1. Operational & Congestion Risks
    if on_time_prob < avoid_on_time_threshold:
        flags.append(f"CRITICAL_DELAY_RISK (On-Time Prob: {on_time_prob*100:.1f}%)")
    elif on_time_prob < on_time_threshold:
        flags.append(f"MODERATE_SCHEDULE_RISK (On-Time Prob: {on_time_prob*100:.1f}%)")
        
    if congestion_idx > 0.75:
        flags.append("HIGH_PORT_CONGESTION_PRESSURE")
        
    if market_regime == "HIGH_VOLATILITY":
        flags.append("MARKET_REGIME_HIGH_VOLATILITY")
        
    # 2. Decision Logic
    if on_time_prob < avoid_on_time_threshold or congestion_idx > 0.85:
        decision = "AVOID"
    elif savings_pct >= savings_threshold_pct and on_time_prob >= on_time_threshold:
        decision = "CHARTER"
    elif market_regime in ["HIGH_VOLATILITY", "FALLING"] or savings_pct < 0:
        decision = "WAIT"
    else:
        decision = "CHARTER" if on_time_prob >= 0.65 else "WAIT"
        
    return decision, flags
