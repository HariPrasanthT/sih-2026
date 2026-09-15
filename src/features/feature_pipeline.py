"""
Master Feature Pipeline Engine.
Assembles all feature groups at forecast timestamp T with zero temporal leakage.
Calculates route nautical distances and produces training master dataset.
"""
import os
import logging
from typing import Optional, Dict, Any, List, Tuple
import pandas as pd
import numpy as np

# pyrefly: ignore [missing-import]
from src.data.port_mapping import CANONICAL_PORTS, normalize_port_name
# pyrefly: ignore [missing-import]
from src.features.freight_features import build_freight_lags_and_rolling
# pyrefly: ignore [missing-import]
from src.features.market_features import build_market_features
# pyrefly: ignore [missing-import]
from src.features.port_features import build_port_features
# pyrefly: ignore [missing-import]
from src.features.vessel_features import build_vessel_features
# pyrefly: ignore [missing-import]
from src.features.temporal_features import build_temporal_features
# pyrefly: ignore [missing-import]
from src.data.manifest import register_dataset

logger = logging.getLogger(__name__)


def calculate_great_circle_distance_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Great Circle distance in nautical miles between coordinates."""
    # Convert to radians
    phi1, lambda1 = np.radians(lat1), np.radians(lon1)
    phi2, lambda2 = np.radians(lat2), np.radians(lon2)
    
    dphi = phi2 - phi1
    dlambda = lambda2 - lambda1
    
    a = np.sin(dphi / 2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2.0)**2
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    
    earth_radius_nm = 3440.065
    return float(earth_radius_nm * c)


def get_route_distance_nm(origin_port: str, dest_port: str) -> float:
    """Get nautical mile distance between origin and destination ports."""
    orig_canon = normalize_port_name(origin_port) or origin_port
    dest_canon = normalize_port_name(dest_port) or dest_port
    
    p1 = CANONICAL_PORTS.get(orig_canon, {})
    p2 = CANONICAL_PORTS.get(dest_canon, {})
    
    if "lat" in p1 and "lat" in p2:
        direct_dist = calculate_great_circle_distance_nm(p1["lat"], p1["lon"], p2["lat"], p2["lon"])
        # Sea routes often navigate through straits (e.g. Malacca, Sunda, Singapore), adding routing factor ~1.15 to 1.30
        routing_factor = 1.22
        return round(direct_dist * routing_factor, 1)
    
    # Fallback standard distances
    route_defaults = {
        ("HAY_POINT", "PARADIP"): 4950.0,
        ("HAY_POINT", "DHAMRA"): 4980.0,
        ("HAY_POINT", "VISAKHAPATNAM"): 4820.0,
        ("GLADSTONE", "PARADIP"): 5100.0,
        ("NEWCASTLE", "PARADIP"): 5400.0,
        ("TANJUNG_BARA", "PARADIP"): 2650.0,
        ("TANJUNG_BARA", "DHAMRA"): 2680.0,
        ("BALIKPAPAN", "PARADIP"): 2580.0,
        ("MAPUTO", "PARADIP"): 4850.0,
        ("RICHARDS_BAY", "PARADIP"): 5150.0,
    }
    return route_defaults.get((orig_canon, dest_canon), 4500.0)


def generate_development_dataset(
    n_days: int = 1200,
    random_seed: int = 42,
    output_parquet: str = "data/processed/master/training_master.parquet"
) -> pd.DataFrame:
    """
    Generate synthetic development dataset for training & testing when real route freight targets are missing.
    Clearly records SYNTHETIC = TRUE in manifest.
    """
    np.random.seed(random_seed)
    
    routes = [
        {"origin": "HAY_POINT", "dest": "PARADIP", "cargo": "Coking Coal", "vclass": "Capesize", "base_freight": 18.5, "base_days": 14.5},
        {"origin": "HAY_POINT", "dest": "DHAMRA", "cargo": "Coking Coal", "vclass": "Capesize", "base_freight": 18.2, "base_days": 14.3},
        {"origin": "HAY_POINT", "dest": "VISAKHAPATNAM", "cargo": "Coking Coal", "vclass": "Capesize", "base_freight": 17.8, "base_days": 14.0},
        {"origin": "GLADSTONE", "dest": "PARADIP", "cargo": "Coking Coal", "vclass": "Panamax", "base_freight": 21.5, "base_days": 15.2},
        {"origin": "NEWCASTLE", "dest": "DHAMRA", "cargo": "Thermal Coal", "vclass": "Panamax", "base_freight": 22.0, "base_days": 16.0},
        {"origin": "TANJUNG_BARA", "dest": "PARADIP", "cargo": "Thermal Coal", "vclass": "Supramax", "base_freight": 11.5, "base_days": 8.0},
        {"origin": "TANJUNG_BARA", "dest": "DHAMRA", "cargo": "Thermal Coal", "vclass": "Supramax", "base_freight": 11.2, "base_days": 7.8},
        {"origin": "BALIKPAPAN", "dest": "KAMARAJAR", "cargo": "Thermal Coal", "vclass": "Supramax", "base_freight": 10.8, "base_days": 7.5},
        {"origin": "MAPUTO", "dest": "VISAKHAPATNAM", "cargo": "Coking Coal", "vclass": "Panamax", "base_freight": 19.5, "base_days": 14.8},
        {"origin": "RICHARDS_BAY", "dest": "PARADIP", "cargo": "Thermal Coal", "vclass": "Capesize", "base_freight": 16.5, "base_days": 15.5},
    ]
    
    start_date = pd.Timestamp("2020-01-01")
    end_date = pd.Timestamp("2026-12-31")
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    
    rows = []
    
    # Generate multi-year macroeconomic background series (2020-2026)
    bdi_series = {}
    bunker_series = {}
    fx_series = {}
    coal_price_series = {}
    
    current_bdi = 1400.0
    current_bunker = 620.0
    current_fx = 74.0
    current_coal = 120.0
    
    for d in date_range:
        # Multi-year historical macro cycles:
        # 2020 COVID dip & recovery; 2021-2022 dry bulk & energy super-cycle; 2023-2026 normalization
        yr = d.year
        if yr == 2020:
            cycle_bdi_bias = -150.0 if d.month <= 6 else 100.0
            cycle_bunker_bias = -100.0 if d.month <= 5 else 0.0
        elif yr in [2021, 2022]:
            cycle_bdi_bias = 800.0  # Dry bulk post-covid commodity boom
            cycle_bunker_bias = 180.0  # 2022 energy shock
        elif yr in [2023, 2024]:
            cycle_bdi_bias = 50.0
            cycle_bunker_bias = 20.0
        else:
            cycle_bdi_bias = 0.0
            cycle_bunker_bias = 0.0
            
        current_bdi += np.random.normal(0, 20) + 0.05 * np.sin(d.dayofyear / 365.0 * 2 * np.pi) + (cycle_bdi_bias - (current_bdi - 1500.0)) * 0.005
        current_bdi = float(np.clip(current_bdi, 700.0, 4800.0))
        
        current_bunker += np.random.normal(0, 3.5) + (cycle_bunker_bias - (current_bunker - 620.0)) * 0.005
        current_bunker = float(np.clip(current_bunker, 380.0, 980.0))
        
        # USD/INR gradual long-term structural trajectory: 73 in 2020 -> 84-88 in 2026
        target_fx = 73.5 + (d.year - 2020) * 2.1 + (d.month / 12.0) * 1.5
        current_fx += np.random.normal(0, 0.04) + (target_fx - current_fx) * 0.02
        current_fx = float(np.clip(current_fx, 72.0, 92.0))
        
        # Coal commodity price index
        current_coal += np.random.normal(0, 1.2) + (140.0 - current_coal) * 0.01
        current_coal = float(np.clip(current_coal, 80.0, 350.0))
        
        bdi_series[d] = round(current_bdi, 1)
        bunker_series[d] = round(current_bunker, 1)
        fx_series[d] = round(current_fx, 2)
        coal_price_series[d] = round(current_coal, 1)
        
    for r in routes:
        orig = r["origin"]
        dest = r["dest"]
        cargo = r["cargo"]
        vclass = r["vclass"]
        base_fr = r["base_freight"]
        base_days = r["base_days"]
        dist_nm = get_route_distance_nm(orig, dest)
        
        current_fr = base_fr
        for d in date_range:
            bdi_val = bdi_series[d]
            bunker_val = bunker_series[d]
            fx_val = fx_series[d]
            coal_val = coal_price_series[d]
            
            # Southwest Monsoon seasonal surge (June-Sept)
            monsoon_mult = 1.08 if d.month in [6, 7, 8, 9] else 1.00
            
            # Fundamental dry bulk market pricing mechanism
            market_factor = (bdi_val / 1500.0) * 0.35 + (bunker_val / 620.0) * 0.30 + (coal_val / 140.0) * 0.10 + 0.25
            
            # Port congestion & waiting days
            cong_idx = round(float(np.clip(0.4 + 0.2 * np.sin(d.dayofyear / 180.0) + np.random.normal(0, 0.1), 0.05, 0.95)), 2)
            port_wait_days = round(float(np.clip(cong_idx * 4.0 + np.random.normal(0, 0.4), 0.5, 6.5)), 1)
            
            # Realistic rate evolution with daily innovation & freight market shocks
            stochastic_shock = np.random.normal(0, 0.45)
            target_fr = base_fr * market_factor * monsoon_mult + (port_wait_days - 2.0) * 0.25 + stochastic_shock
            current_fr = 0.80 * current_fr + 0.20 * target_fr
            freight_usd = round(float(max(4.5, current_fr)), 2)
            
            # Voyage transit duration
            transit_days = round(float(max(3.0, base_days + (port_wait_days - 2.0) * 0.4 + np.random.normal(0, 0.5))), 1)
            on_time_flag = int(transit_days <= (base_days + 1.5))
            
            # Weather variables
            is_monsoon_m = d.month in [6, 7, 8, 9]
            wave_h = round(float(np.clip(np.random.normal(2.2, 0.5) if is_monsoon_m else np.random.normal(1.2, 0.3), 0.5, 5.0)), 2)
            wind_kts = round(float(np.clip(np.random.normal(22, 5) if is_monsoon_m else np.random.normal(12, 3), 4, 45)), 1)
            cyclone_alert = int(d.month in [5, 6, 10, 11] and np.random.rand() < 0.12)
            
            # Market indices
            volatility_idx = round(float(np.clip(np.random.normal(20.0, 4.0), 10.0, 50.0)), 2)
            demand_idx = round(float(np.clip((bdi_val / 1500.0) * 100.0 + np.random.normal(0, 5.0), 50.0, 180.0)), 1)
            
            rows.append({
                "forecast_date": d,
                "origin_port": orig,
                "destination_port": dest,
                "cargo_type": cargo,
                "vessel_class": vclass,
                "route_distance_nm": dist_nm,
                "bdi_index": bdi_val,
                "bunker_vlsfo_usd_ton": bunker_val,
                "usd_inr_rate": fx_val,
                "coal_benchmark_usd_ton": coal_val,
                "wave_height_m": wave_h,
                "wind_speed_knots": wind_kts,
                "cyclone_alert_flag": cyclone_alert,
                "volatility_index": volatility_idx,
                "demand_index": demand_idx,
                "derived_congestion_index": cong_idx,
                "est_waiting_days": port_wait_days,
                "vessels_approaching_count": int(np.random.poisson(8)),
                "vessels_anchorage_count": int(np.random.poisson(12)),
                "freight_usd_per_ton": freight_usd,
                "transit_days": transit_days,
                "on_time_flag": on_time_flag
            })
            
    df_raw = pd.DataFrame(rows)
    
    # Apply feature pipeline
    logger.info("Applying feature engineering pipeline...")
    df_feat = build_freight_lags_and_rolling(
        df_raw,
        target_col="freight_usd_per_ton",
        group_cols=["origin_port", "destination_port", "vessel_class"],
        time_col="forecast_date"
    )
    df_feat = build_market_features(df_feat, time_col="forecast_date")
    df_feat = build_port_features(df_feat)
    df_feat = build_temporal_features(df_feat, date_col="forecast_date")
    
    # Save synthetic development master
    synth_path = "data/synthetic/development_only/synthetic_training_master.parquet"
    os.makedirs(os.path.dirname(synth_path), exist_ok=True)
    df_feat.to_parquet(synth_path, index=False)
    
    # Save processed master table
    os.makedirs(os.path.dirname(output_parquet), exist_ok=True)
    df_feat.to_parquet(output_parquet, index=False)
    
    register_dataset(
        dataset_name="training_master",
        local_path=output_parquet,
        source_type="SYNTHETIC",
        scope="SYNTHETIC_DEVELOPMENT_ONLY",
        intended_use="Model training, walk-forward validation, and pipeline verification for SIH 26006",
        rows=len(df_feat),
        columns=list(df_feat.columns),
        limitations="Explicit synthetic development dataset. Separated from real government port data."
    )
    
    logger.info(f"Training master table generated ({len(df_feat)} rows) saved to {output_parquet}")
    return df_feat


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_development_dataset()
