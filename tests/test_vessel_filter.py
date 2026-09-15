"""
Unit tests for vessel feasibility filtering engine and physical port constraints.
"""
import pytest
import pandas as pd
# pyrefly: ignore [missing-import]
from src.optimization.vessel_filter import check_vessel_port_compatibility, filter_feasible_vessels


def test_vessel_status_available():
    vessel = {
        "vessel_id": "V1",
        "status": "maintenance",
        "dwt": 80000,
        "draft_m": 14.0,
        "loa_m": 225.0,
        "beam_m": 32.2,
        "vessel_class": "Panamax"
    }
    is_feas, reasons = check_vessel_port_compatibility(vessel, "PARADIP", 70000)
    assert not is_feas
    assert any("status" in r for r in reasons)


def test_vessel_dwt_capacity_constraint():
    vessel = {
        "vessel_id": "V2",
        "status": "available",
        "dwt": 50000,
        "draft_m": 12.0,
        "loa_m": 190.0,
        "beam_m": 32.2,
        "vessel_class": "Supramax"
    }
    # Cargo is 70,000 MT which exceeds DWT 50,000
    is_feas, reasons = check_vessel_port_compatibility(vessel, "PARADIP", 70000)
    assert not is_feas
    assert any("exceeds vessel DWT" in r for r in reasons)


def test_vessel_draft_exceeds_port_limit():
    vessel = {
        "vessel_id": "V3",
        "status": "available",
        "dwt": 180000,
        "draft_m": 18.5,  # Exceeds Paradip 17.1m
        "loa_m": 292.0,
        "beam_m": 45.0,
        "vessel_class": "Capesize"
    }
    is_feas, reasons = check_vessel_port_compatibility(vessel, "PARADIP", 150000)
    assert not is_feas
    assert any("Draft" in r for r in reasons)


def test_vessel_loa_exceeds_port_limit():
    vessel = {
        "vessel_id": "V4",
        "status": "available",
        "dwt": 90000,
        "draft_m": 13.5,
        "loa_m": 310.0,  # Exceeds Paradip max LOA 300m
        "beam_m": 38.0,
        "vessel_class": "Panamax"
    }
    is_feas, reasons = check_vessel_port_compatibility(vessel, "PARADIP", 75000)
    assert not is_feas
    assert any("LOA" in r for r in reasons)


def test_vessel_class_forbidden_at_port():
    vessel = {
        "vessel_id": "V5",
        "status": "available",
        "dwt": 180000,
        "draft_m": 11.0,
        "loa_m": 200.0,
        "beam_m": 32.0,
        "vessel_class": "Capesize"
    }
    # Kolkata only permits Handysize and Supramax
    is_feas, reasons = check_vessel_port_compatibility(vessel, "KOLKATA", 30000)
    assert not is_feas
    assert any("not permitted" in r for r in reasons)


def test_filter_feasible_vessels_partition():
    candidates = pd.DataFrame([
        {"vessel_id": "V_FEAS", "status": "available", "dwt": 82000, "draft_m": 14.2, "loa_m": 229.0, "beam_m": 32.2, "vessel_class": "Panamax"},
        {"vessel_id": "V_DRAFT", "status": "available", "dwt": 180000, "draft_m": 19.0, "loa_m": 290.0, "beam_m": 45.0, "vessel_class": "Capesize"},
        {"vessel_id": "V_MAINT", "status": "maintenance", "dwt": 82000, "draft_m": 14.2, "loa_m": 229.0, "beam_m": 32.2, "vessel_class": "Panamax"}
    ])
    df_feas, df_excl = filter_feasible_vessels(candidates, "PARADIP", 75000)
    assert len(df_feas) == 1
    assert df_feas.iloc[0]["vessel_id"] == "V_FEAS"
    assert len(df_excl) == 2
