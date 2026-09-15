"""
Port Congestion, Turnaround, and Operations Feature Engineering.
"""
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def build_port_features(
    df: pd.DataFrame,
    port_col: str = "destination_port",
    congestion_col: str = "derived_congestion_index",
    waiting_col: str = "est_waiting_days"
) -> pd.DataFrame:
    """
    Generate port congestion, queuing, and turnaround interaction features.
    """
    df_out = df.copy()
    
    if congestion_col in df_out.columns:
        df_out["congestion_severity_level"] = pd.cut(
            df_out[congestion_col],
            bins=[-0.1, 0.35, 0.70, 1.1],
            labels=["LOW", "MODERATE", "HIGH"]
        ).astype(str)
        
    if waiting_col in df_out.columns:
        df_out["waiting_pressure_ratio"] = df_out[waiting_col] / 3.0  # relative to 3 days baseline
        
    if congestion_col in df_out.columns:
        df_out["congestion_score"] = (df_out[congestion_col].clip(0.0, 1.0) * 100.0).round(1)

    # Typical drafts and LOAs by vessel class
    typical_drafts = {"Capesize": 18.2, "Panamax": 14.5, "Supramax": 12.8, "Handysize": 10.0}
    typical_loas = {"Capesize": 292.0, "Panamax": 225.0, "Supramax": 190.0, "Handysize": 180.0}
    
    # Port maximum limits
    port_max_drafts = {"PARADIP": 17.5, "DHAMRA": 18.5, "VISAKHAPATNAM": 18.1, "GANGAVARAM": 18.5,
                       "KAMARAJAR": 16.0, "CHENNAI": 15.5, "HALDIA": 8.5}
    port_max_loas = {"PARADIP": 300.0, "DHAMRA": 320.0, "VISAKHAPATNAM": 300.0, "GANGAVARAM": 320.0,
                     "KAMARAJAR": 280.0, "CHENNAI": 275.0, "HALDIA": 230.0}
    
    v_class = df_out.get("vessel_class", pd.Series(["Panamax"] * len(df_out)))
    dest_p = df_out.get(port_col, pd.Series(["PARADIP"] * len(df_out)))
    
    v_draft = v_class.map(typical_drafts).fillna(14.5)
    v_loa = v_class.map(typical_loas).fillna(225.0)
    p_draft = dest_p.map(port_max_drafts).fillna(16.0)
    p_loa = dest_p.map(port_max_loas).fillna(280.0)
    
    df_out["draft_utilization"] = (v_draft / p_draft).round(3)
    df_out["loa_utilization"] = (v_loa / p_loa).round(3)
    
    return df_out
