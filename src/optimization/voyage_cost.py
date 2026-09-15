"""
Voyage Economics and Total Cost Modeling Engine.
Computes comprehensive voyage economics (freight + bunker + port dues + waiting/demurrage risk)
and evaluates savings relative to feasible market average.
"""
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def compute_voyage_economics(
    candidates_df: pd.DataFrame,
    freight_rate_p10: float,
    freight_rate_p50: float,
    freight_rate_p90: float,
    cargo_size_tons: float = 70000.0,
    bunker_price_usd: float = 620.0,
    est_waiting_days: float = 2.0
) -> pd.DataFrame:
    """
    Calculate full voyage cost breakdown for all candidate vessels.
    Computes market_avg_cost across ALL feasible candidates.
    """
    if candidates_df.empty:
        return candidates_df
        
    df = candidates_df.copy()
    
    # 1. Base Freight Component (USD)
    df["freight_cost_p10"] = cargo_size_tons * freight_rate_p10
    df["freight_cost_p50"] = cargo_size_tons * freight_rate_p50
    df["freight_cost_p90"] = cargo_size_tons * freight_rate_p90
    
    # 2. Bunker Cost Component (USD) = Sea Consumption * Transit Days * Bunker Price
    transit_days = df.get("estimated_transit_days", pd.Series(14.0, index=df.index))
    sea_fuel = df.get("fuel_consumption_sea_t_day", pd.Series(28.0, index=df.index))
    df["bunker_cost_usd"] = (sea_fuel * transit_days * bunker_price_usd).round(2)
    
    # 3. Port Dues & Berth Charges (approx. 1.20 USD per DWT)
    dwt = df.get("dwt", pd.Series(75000, index=df.index))
    df["port_dues_usd"] = (dwt * 1.20).round(2)
    
    # 4. Anchorage Waiting & Idling Cost
    daily_hire = df.get("daily_hire_rate_usd", pd.Series(18000, index=df.index))
    df["waiting_cost_usd"] = (est_waiting_days * daily_hire).round(2)
    
    # 5. Total Estimated Voyage Cost (P10, P50, P90)
    df["predicted_cost_low"] = (df["freight_cost_p10"] + df["bunker_cost_usd"] + df["port_dues_usd"] + df["waiting_cost_usd"]).round(2)
    df["predicted_cost_median"] = (df["freight_cost_p50"] + df["bunker_cost_usd"] + df["port_dues_usd"] + df["waiting_cost_usd"]).round(2)
    df["predicted_cost_high"] = (df["freight_cost_p90"] + df["bunker_cost_usd"] + df["port_dues_usd"] + df["waiting_cost_usd"]).round(2)
    
    # 6. Market Average Cost: Mean median predicted cost across ALL feasible candidates
    market_avg = float(df["predicted_cost_median"].mean())
    df["market_avg_cost"] = round(market_avg, 2)
    
    # 7. Savings Percentage vs Market Average
    df["savings_vs_market_pct"] = (((market_avg - df["predicted_cost_median"]) / market_avg) * 100.0).round(2)
    
    return df
