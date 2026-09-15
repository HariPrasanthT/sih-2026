"""
Unit tests for port physical constraints and vessel compatibility filtering.
"""
import pytest
# pyrefly: ignore [missing-import]
from src.optimization.port_compatibility import check_vessel_port_compatibility


def test_vessel_port_draft_violation():
    # Dhamra max draft is 18.0m. A vessel with draft 18.5m must fail.
    vessel = {
        "vessel_id": "VSL_DRAFT_FAIL",
        "dwt": 150000,
        "draft_m": 18.5,
        "loa_m": 290.0,
        "beam_m": 45.0,
        "vessel_class": "Capesize",
        "status": "available"
    }
    is_feasible, reasons = check_vessel_port_compatibility(vessel, port_name="DHAMRA", cargo_size_tons=70000)
    assert is_feasible is False
    assert any("Draft" in r for r in reasons)


def test_vessel_port_loa_violation():
    # Haldia max LOA is 230m. A vessel with LOA 290m must fail.
    vessel = {
        "vessel_id": "VSL_LOA_FAIL",
        "dwt": 40000,
        "draft_m": 8.0,
        "loa_m": 290.0,
        "beam_m": 30.0,
        "vessel_class": "Handysize",
        "status": "available"
    }
    is_feasible, reasons = check_vessel_port_compatibility(vessel, port_name="HALDIA", cargo_size_tons=35000)
    assert is_feasible is False
    assert any("LOA" in r for r in reasons)


def test_vessel_status_unavailable():
    vessel = {
        "vessel_id": "VSL_UNAVAIL",
        "dwt": 75000,
        "draft_m": 13.5,
        "loa_m": 225.0,
        "beam_m": 32.2,
        "vessel_class": "Panamax",
        "status": "on_voyage"
    }
    is_feasible, reasons = check_vessel_port_compatibility(vessel, port_name="PARADIP", cargo_size_tons=70000)
    assert is_feasible is False
    assert any("available" in r for r in reasons)


def test_vessel_feasible_case():
    vessel = {
        "vessel_id": "VSL_OK",
        "dwt": 75000,
        "draft_m": 13.5,
        "loa_m": 225.0,
        "beam_m": 32.2,
        "vessel_class": "Panamax",
        "status": "available"
    }
    is_feasible, reasons = check_vessel_port_compatibility(vessel, port_name="PARADIP", cargo_size_tons=70000)
    assert is_feasible is True
    assert len(reasons) == 0
