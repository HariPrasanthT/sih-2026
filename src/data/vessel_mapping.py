"""
Vessel Classification, Specifications, and Master Fleet Registry.
"""
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

VESSEL_CLASSES: Dict[str, Dict[str, Any]] = {
    "Handysize": {
        "dwt_min": 10000,
        "dwt_max": 39999,
        "typical_dwt": 32000,
        "typical_loa_m": 170.0,
        "typical_beam_m": 27.0,
        "typical_draft_m": 9.8,
        "design_speed_knots": 13.5,
        "fuel_consumption_sea_t_day": 18.0,
        "fuel_consumption_port_t_day": 2.5,
        "daily_charter_base_usd": 12500,
    },
    "Supramax": {
        "dwt_min": 40000,
        "dwt_max": 64999,
        "typical_dwt": 55000,
        "typical_loa_m": 190.0,
        "typical_beam_m": 32.2,
        "typical_draft_m": 12.8,
        "design_speed_knots": 14.0,
        "fuel_consumption_sea_t_day": 24.0,
        "fuel_consumption_port_t_day": 3.0,
        "daily_charter_base_usd": 16000,
    },
    "Panamax": {
        "dwt_min": 65000,
        "dwt_max": 99999,
        "typical_dwt": 75000,
        "typical_loa_m": 225.0,
        "typical_beam_m": 32.2,
        "typical_draft_m": 14.2,
        "design_speed_knots": 14.5,
        "fuel_consumption_sea_t_day": 31.0,
        "fuel_consumption_port_t_day": 3.5,
        "daily_charter_base_usd": 19500,
    },
    "Capesize": {
        "dwt_min": 100000,
        "dwt_max": 350000,
        "typical_dwt": 180000,
        "typical_loa_m": 290.0,
        "typical_beam_m": 45.0,
        "typical_draft_m": 18.2,
        "design_speed_knots": 14.5,
        "fuel_consumption_sea_t_day": 48.0,
        "fuel_consumption_port_t_day": 4.5,
        "daily_charter_base_usd": 28000,
    }
}


def classify_vessel_by_dwt(dwt: float) -> str:
    """Determine vessel class from Deadweight Tonnage (DWT)."""
    if pd.isna(dwt) or dwt <= 0:
        return "Unknown"
    for vclass, specs in VESSEL_CLASSES.items():
        if specs["dwt_min"] <= dwt <= specs["dwt_max"]:
            return vclass
    if dwt > 350000:
        return "VLOC"
    return "Small_Bulk"


def generate_candidate_fleet(n_vessels: int = 30, random_seed: int = 42) -> pd.DataFrame:
    """Generate a realistic master candidate fleet for charter evaluation."""
    np.random.seed(random_seed)
    vessels = []
    
    classes = ["Handysize", "Supramax", "Panamax", "Capesize"]
    weights = [0.20, 0.30, 0.35, 0.15]
    
    names_prefix = ["MV OCEAN", "MV STEEL", "MV BHARAT", "MV EASTERN", "MV PACIFIC", "MV VISHAL", "MV GLOBAL"]
    names_suffix = ["LEADER", "TRADER", "CARRIER", "VOYAGER", "PIONEER", "NAVIGATOR", "ENTERPRISE", "FORTUNE"]
    
    used_names = set()
    
    for i in range(1, n_vessels + 1):
        vclass = np.random.choice(classes, p=weights)
        specs = VESSEL_CLASSES[vclass]
        
        dwt = int(np.random.uniform(specs["dwt_min"] + 1000, specs["dwt_max"] - 1000))
        loa = round(specs["typical_loa_m"] + np.random.uniform(-10, 15), 1)
        beam = round(specs["typical_beam_m"] + np.random.uniform(-1.5, 2.5), 1)
        draft = round(specs["typical_draft_m"] + np.random.uniform(-0.8, 1.2), 2)
        speed = round(specs["design_speed_knots"] + np.random.uniform(-0.8, 0.8), 1)
        fuel_sea = round(specs["fuel_consumption_sea_t_day"] * (1 + np.random.uniform(-0.1, 0.1)), 1)
        fuel_port = round(specs["fuel_consumption_port_t_day"] * (1 + np.random.uniform(-0.1, 0.1)), 1)
        age = int(np.random.uniform(2, 22))
        
        # Unique name
        while True:
            name = f"{np.random.choice(names_prefix)} {np.random.choice(names_suffix)} {i}"
            if name not in used_names:
                used_names.add(name)
                break
        
        imo = 9000000 + i * 137
        mmsi = 419000000 + i * 97
        
        status = np.random.choice(["available", "available", "available", "on_voyage", "in_maintenance"], p=[0.75, 0.10, 0.05, 0.05, 0.05])
        
        vessels.append({
            "vessel_id": f"VSL_{imo}",
            "vessel_name": name,
            "imo": imo,
            "mmsi": mmsi,
            "vessel_class": vclass,
            "dwt": dwt,
            "loa_m": loa,
            "beam_m": beam,
            "draft_m": draft,
            "design_speed_knots": speed,
            "fuel_consumption_sea_t_day": fuel_sea,
            "fuel_consumption_port_t_day": fuel_port,
            "vessel_age_years": age,
            "status": status,
            "current_location": np.random.choice(["Bay of Bengal", "Singapore Strait", "Indian Ocean", "East Coast India", "Australia Coast"]),
            "eta_days_to_load_port": round(float(np.random.uniform(1.0, 7.0)), 1),
            "daily_hire_rate_usd": round(specs["daily_charter_base_usd"] * (1 + np.random.uniform(-0.15, 0.15)), 2)
        })
        
    df = pd.DataFrame(vessels)
    return df


def export_vessel_master_table(output_dir: str = "data/processed/vessel") -> None:
    """Generate vessel_master.parquet."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    df = generate_candidate_fleet(40)
    out_path = os.path.join(output_dir, "vessel_master.parquet")
    df.to_parquet(out_path, index=False)
    logger.info(f"Vessel master table exported to {out_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    export_vessel_master_table()
