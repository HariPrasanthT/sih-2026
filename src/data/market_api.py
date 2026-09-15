"""
Live Market & Macroeconomic API Client (Alpha Vantage & Fallback).
Fetches real-time USD/INR exchange rates, crude oil benchmarks, and commodity indicators.
Falls back safely to local historical benchmarks if offline or rate-limited.
"""
import os
import logging
from typing import Optional, Dict, Any
import requests

logger = logging.getLogger(__name__)


def _get_env_key(key_name: str) -> str:
    """Retrieve key from os.environ or directly from .env file."""
    val = os.environ.get(key_name, "").strip()
    if val:
        return val
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{key_name}="):
                        return line.split("=", 1)[1].strip()
        except Exception:
            pass
    return ""


def get_alpha_vantage_api_key() -> str:
    """Retrieve Alpha Vantage API key from environment or .env."""
    return _get_env_key("ALPHA_VANTAGE_API_KEY")


def get_fred_api_key() -> str:
    """Retrieve FRED API key from environment or .env."""
    return _get_env_key("FRED_API_KEY")


def fetch_live_usd_inr_rate(default_rate: float = 83.50) -> float:
    """
    Fetch current real-time USD to INR foreign exchange rate from Alpha Vantage.
    Returns default_rate if key missing, API throttled, or network unavailable.
    """
    api_key = get_alpha_vantage_api_key()
    if not api_key:
        logger.debug("ALPHA_VANTAGE_API_KEY not configured. Using default rate.")
        return default_rate

    url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=INR&apikey={api_key}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if "Realtime Currency Exchange Rate" in data:
                rate_str = data["Realtime Currency Exchange Rate"].get("5. Exchange Rate")
                if rate_str:
                    rate = round(float(rate_str), 2)
                    logger.info(f"Live USD/INR rate retrieved from Alpha Vantage: {rate}")
                    return rate
            elif "Note" in data:
                logger.warning(f"Alpha Vantage rate limit reached: {data['Note']}")
    except Exception as e:
        logger.warning(f"Failed to fetch live USD/INR from Alpha Vantage: {e}")

    return default_rate


def fetch_live_brent_crude(default_price: float = 78.50) -> float:
    """
    Fetch live monthly Brent Crude Oil price from Alpha Vantage.
    Returns default_price if unavailable.
    """
    api_key = get_alpha_vantage_api_key()
    if not api_key:
        return default_price

    url = f"https://www.alphavantage.co/query?function=BRENT&interval=monthly&apikey={api_key}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if "data" in data and len(data["data"]) > 0:
                val = data["data"][0].get("value")
                if val and val != ".":
                    price = round(float(val), 2)
                    logger.info(f"Live Brent crude price retrieved: ${price}/barrel")
                    return price
    except Exception as e:
        logger.warning(f"Failed to fetch live Brent crude: {e}")

    return default_price


def fetch_fred_series(series_id: str = "DCOILBRENTEU", default_val: float = 80.0) -> float:
    """
    Fetch the most recent economic observation from the St. Louis Fed FRED API.
    Common series:
      - 'DCOILBRENTEU': Crude Oil Prices: Brent - Europe (USD/Barrel)
      - 'DEXINUS': U.S. Dollars to Indian Rupee Spot Exchange Rate
      - 'DCOILWTICO': Crude Oil Prices: West Texas Intermediate (WTI)
    """
    api_key = get_fred_api_key()
    if not api_key:
        logger.debug("FRED_API_KEY not configured. Using default series value.")
        return default_val

    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json&sort_order=desc&limit=5"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            observations = data.get("observations", [])
            for obs in observations:
                val = obs.get("value")
                if val and val != ".":
                    numeric_val = round(float(val), 2)
                    logger.info(f"FRED series {series_id} latest value ({obs.get('date')}): {numeric_val}")
                    return numeric_val
    except Exception as e:
        logger.warning(f"Failed to fetch FRED series {series_id}: {e}")

    return default_val
