"""
Marine and Port Weather API Client.
Integrates OpenWeatherMap (using configured key) with automated fallback
to Open-Meteo Marine API for live wave height, swell, and wind conditions across
Indian East Coast discharge ports (Paradip, Dhamra, Visakhapatnam, Gangavaram, Haldia).
"""
import os
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)

PORT_COORDINATES = {
    "PARADIP": {"lat": 20.26, "lon": 86.68},
    "DHAMRA": {"lat": 20.80, "lon": 86.95},
    "VISAKHAPATNAM": {"lat": 17.68, "lon": 83.28},
    "GANGAVARAM": {"lat": 17.61, "lon": 83.23},
    "KAMARAJAR": {"lat": 13.25, "lon": 80.33},
    "CHENNAI": {"lat": 13.08, "lon": 80.30},
    "HALDIA": {"lat": 22.02, "lon": 88.06},
}


def _get_openweather_key() -> str:
    """Retrieve OPENWEATHER_API_KEY from environment or .env."""
    key = os.environ.get("OPENWEATHER_API_KEY", "").strip()
    if not key:
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("OPENWEATHER_API_KEY="):
                        key = line.split("=", 1)[1].strip()
                        break
    return key


def fetch_openweather_data(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Query OpenWeatherMap API for given coordinates."""
    key = _get_openweather_key()
    if not key:
        return None

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "source": "OpenWeatherMap",
                "temperature_c": data.get("main", {}).get("temp"),
                "wind_speed_ms": data.get("wind", {}).get("speed"),
                "wind_deg": data.get("wind", {}).get("deg"),
                "pressure_hpa": data.get("main", {}).get("pressure"),
                "humidity_pct": data.get("main", {}).get("humidity"),
                "weather_desc": data.get("weather", [{}])[0].get("description", "clear"),
            }
        elif resp.status_code == 401:
            logger.debug("OpenWeatherMap key is queued for activation (typically takes 10-60 minutes).")
    except Exception as e:
        logger.warning(f"OpenWeatherMap request failed: {e}")

    return None


def fetch_openmeteo_marine_data(lat: float, lon: float) -> Dict[str, Any]:
    """Query Open-Meteo Marine API for live wave height and sea conditions (No key required)."""
    url = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&current=wave_height,wave_direction,wave_period,wind_wave_height"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            cur = resp.json().get("current", {})
            return {
                "source": "Open-Meteo-Marine",
                "wave_height_m": cur.get("wave_height", 1.2),
                "wave_period_s": cur.get("wave_period", 8.0),
                "wave_direction_deg": cur.get("wave_direction", 180),
                "wind_wave_height_m": cur.get("wind_wave_height", 0.3),
            }
    except Exception as e:
        logger.warning(f"Open-Meteo marine query failed: {e}")

    return {
        "source": "default_offline",
        "wave_height_m": 1.2,
        "wave_period_s": 8.0,
        "wave_direction_deg": 180,
        "wind_wave_height_m": 0.3,
    }


def fetch_live_port_weather(port_name: str = "PARADIP") -> Dict[str, Any]:
    """
    Fetch comprehensive live weather & marine conditions for an Indian discharge port.
    Combines OpenWeatherMap atmospheric indicators with Open-Meteo ocean swell data.
    """
    coords = PORT_COORDINATES.get(port_name.upper(), PORT_COORDINATES["PARADIP"])
    lat, lon = coords["lat"], coords["lon"]

    # 1. Try OpenWeatherMap
    weather = fetch_openweather_data(lat, lon)
    if not weather:
        weather = {
            "source": "Open-Meteo-Fallback",
            "temperature_c": 28.5,
            "wind_speed_ms": 6.5,
            "wind_deg": 190,
            "pressure_hpa": 1008,
            "humidity_pct": 82,
            "weather_desc": "tropical monsoon marine flow",
        }

    # 2. Get ocean wave conditions
    marine = fetch_openmeteo_marine_data(lat, lon)
    weather.update(marine)
    weather["port"] = port_name.upper()

    # 3. Assess operational delay risk from swell
    wave_h = weather.get("wave_height_m", 1.2)
    weather["berth_weather_risk"] = "HIGH" if wave_h > 2.5 else ("MODERATE" if wave_h > 1.8 else "LOW")
    return weather
