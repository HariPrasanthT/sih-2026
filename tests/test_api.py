"""
Integration and API endpoint tests using FastAPI TestClient.
"""
import pytest
from fastapi.testclient import TestClient
# pyrefly: ignore [missing-import]
from src.api.app import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OPERATIONAL"


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "model_version" in data


def test_ports_endpoint():
    response = client.get("/ports")
    assert response.status_code == 200
    ports = response.json()
    assert len(ports) >= 7
    codes = [p["port_code"] for p in ports]
    assert "PARADIP" in codes
    assert "DHAMRA" in codes


def test_model_metrics_endpoint():
    response = client.get("/model/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data


def test_recommendations_endpoint_australia_dhamra():
    payload = {
        "origin_port": "HAY_POINT",
        "destination_port": "DHAMRA",
        "cargo_type": "Coking Coal",
        "cargo_size_tons": 70000.0,
        "ship_date": "2026-09-15",
        "weight_cost": 0.50,
        "weight_speed": 0.30,
        "weight_reliability": 0.20,
        "top_n": 5
    }
    response = client.post("/recommendations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["origin_port"] == "HAY_POINT"
    assert data["destination_port"] == "DHAMRA"
    assert data["freight_low"] <= data["freight_median"] <= data["freight_high"]
    assert len(data["recommendations"]) <= 5
    assert len(data["recommendations"]) >= 1
    top_ship = data["recommendations"][0]
    assert top_ship["rank"] == 1
    assert top_ship["decision"] in ["CHARTER", "WAIT", "AVOID"]


def test_live_market_endpoint():
    response = client.get("/live/market")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "LIVE"
    assert "usd_inr_rate" in data
    assert "brent_crude_usd_bbl" in data


def test_live_weather_endpoint():
    response = client.get("/live/weather?port=PARADIP")
    assert response.status_code == 200
    data = response.json()
    assert data["port"] == "PARADIP"
    assert "wave_height_m" in data or "temperature_c" in data


def test_live_coal_dispatch_endpoint():
    response = client.get("/live/coal-dispatch")
    assert response.status_code == 200
    data = response.json()
    assert "records_count" in data
    assert data["records_count"] > 0


def test_live_fleet_endpoint():
    response = client.get("/live/fleet")
    assert response.status_code == 200
    data = response.json()
    assert "vessel_count" in data
    assert data["vessel_count"] > 0


def test_forecast_endpoint():
    response = client.get("/forecast?origin_port=NEWCASTLE&destination_port=DHAMRA&days=30")
    assert response.status_code == 200
    data = response.json()
    assert "corridor" in data
    assert "points" in data
    assert len(data["points"]) > 0
    assert "current_rate" in data
    assert "confidence_score" in data
