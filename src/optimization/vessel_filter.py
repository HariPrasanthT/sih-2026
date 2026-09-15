"""
Vessel Feasibility Filtering Engine for Indian East Coast Ports.
Enforces hard physical constraints: draft, LOA, beam, DWT, vessel class, and availability status.
Returns feasible candidates and explicit exclusion reason codes for auditability.
"""
import logging
from typing import Dict, Any, List, Tuple
import pandas as pd

# pyrefly: ignore [missing-import]
from src.data.port_mapping import get_port_constraints, normalize_port_name

logger = logging.getLogger(__name__)


def check_vessel_port_compatibility(
    vessel: Dict[str, Any],
    port_name: str,
    cargo_size_tons: float = 70000.0,
    cargo_type: str = "Coking Coal"
) -> Tuple[bool, List[str]]:
    """
    Evaluate hard physical compatibility between a vessel candidate and an Indian discharge port.
    Returns (is_feasible, list_of_exclusion_reasons).
    """
    reasons = []
    canonical_port = normalize_port_name(port_name) or port_name
    constraints = get_port_constraints(canonical_port)
    
    if not constraints:
        reasons.append(f"Port '{port_name}' not found in canonical Indian East Coast registry.")
        return False, reasons
        
    # 1. Availability Status Check
    status = str(vessel.get("status", "available")).lower()
    if status != "available":
        reasons.append(f"Vessel status is '{status}' (must be 'available').")
        
    # 2. Cargo Size vs Vessel DWT
    dwt = float(vessel.get("dwt", 0))
    if dwt < cargo_size_tons:
        reasons.append(f"Cargo size ({cargo_size_tons:,.0f} MT) exceeds vessel DWT ({dwt:,.0f} MT).")
        
    # 3. Maximum Draft Constraint
    vessel_draft = float(vessel.get("draft_m", 0))
    port_max_draft = float(constraints.get("max_draft_m", 15.0))
    if vessel_draft > port_max_draft:
        reasons.append(f"Draft {vessel_draft:.2f}m > port maximum limit {port_max_draft:.2f}m at {canonical_port}.")
        
    # 4. Maximum LOA (Length Overall) Constraint
    vessel_loa = float(vessel.get("loa_m", 0))
    port_max_loa = float(constraints.get("max_loa_m", 300.0))
    if vessel_loa > port_max_loa:
        reasons.append(f"LOA {vessel_loa:.1f}m > port maximum limit {port_max_loa:.1f}m at {canonical_port}.")
        
    # 5. Maximum Beam Constraint
    vessel_beam = float(vessel.get("beam_m", 0))
    port_max_beam = float(constraints.get("max_beam_m", 50.0))
    if vessel_beam > port_max_beam:
        reasons.append(f"Beam {vessel_beam:.1f}m > port maximum limit {port_max_beam:.1f}m at {canonical_port}.")
        
    # 6. Allowed Vessel Class at Port
    vclass = str(vessel.get("vessel_class", "Unknown"))
    allowed_classes = constraints.get("allowed_vessel_classes", [])
    if allowed_classes and vclass not in allowed_classes:
        reasons.append(f"Vessel class '{vclass}' is not permitted at {canonical_port} (allowed: {allowed_classes}).")
        
    is_feasible = len(reasons) == 0
    return is_feasible, reasons


def filter_feasible_vessels(
    candidates_df: pd.DataFrame,
    destination_port: str,
    cargo_size_tons: float = 70000.0,
    cargo_type: str = "Coking Coal"
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Partition candidate fleet into (feasible_df, excluded_df) with audit trails.
    """
    if candidates_df.empty:
        return pd.DataFrame(), pd.DataFrame()
        
    feasible_records = []
    excluded_records = []
    
    for _, row in candidates_df.iterrows():
        vessel_dict = row.to_dict()
        is_feasible, reasons = check_vessel_port_compatibility(
            vessel_dict,
            port_name=destination_port,
            cargo_size_tons=cargo_size_tons,
            cargo_type=cargo_type
        )
        
        vessel_dict["port_feasible"] = is_feasible
        vessel_dict["exclusion_reasons"] = reasons
        
        if is_feasible:
            feasible_records.append(vessel_dict)
        else:
            excluded_records.append(vessel_dict)
            
    df_feas = pd.DataFrame(feasible_records) if feasible_records else pd.DataFrame()
    df_excl = pd.DataFrame(excluded_records) if excluded_records else pd.DataFrame()
    
    logger.info(f"Port compatibility filter: {len(df_feas)} feasible, {len(df_excl)} excluded for {destination_port}")
    return df_feas, df_excl
