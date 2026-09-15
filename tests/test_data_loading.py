"""
Unit tests for data loading and manifest validation.
"""
import pytest
import pandas as pd
# pyrefly: ignore [missing-import]
from src.data.loaders import load_port_master, load_vessel_master, load_port_congestion
# pyrefly: ignore [missing-import]
from src.data.port_mapping import normalize_port_name


def test_load_port_master():
    df = load_port_master()
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 9
    assert "port_code" in df.columns
    assert "max_draft_m" in df.columns
    assert "PARADIP" in df["port_code"].values
    assert "DHAMRA" in df["port_code"].values


def test_load_vessel_master():
    df = load_vessel_master()
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 20
    assert "vessel_id" in df.columns
    assert "dwt" in df.columns
    assert "draft_m" in df.columns
    assert "status" in df.columns


def test_port_name_normalization():
    assert normalize_port_name("Paradip Port") == "PARADIP"
    assert normalize_port_name("Vizag") == "VISAKHAPATNAM"
    assert normalize_port_name("Dhamra") == "DHAMRA"
    assert normalize_port_name("Chennai Port") == "CHENNAI"
    assert normalize_port_name("NonExistentPort123") is None


def test_parse_aishub_csv_record():
    # pyrefly: ignore [missing-import]
    from src.data.ais_api import parse_aishub_csv_record, query_live_aishub_vessels

    sample_row = {
        "MMSI": "311733000",
        "TSTAMP": "1625832485",
        "LATITUDE": "10807900",
        "LONGITUDE": "-37828000",
        "COG": "487",
        "SOG": "0",
        "HEADING": "49",
        "NAVSTAT": "5",
        "IMO": "9111802",
        "NAME": '"ENCHANTMENT OTS"',
        "CALLSIGN": "C6FZ7",
        "TYPE": "60",
        "DRAUGHT": "72",
        "DEST": '"PHILIPSBURG"',
    }
    parsed = parse_aishub_csv_record(sample_row)
    assert parsed["mmsi"] == 311733000
    assert parsed["imo"] == 9111802
    assert parsed["vessel_name"] == "ENCHANTMENT OTS"
    assert parsed["callsign"] == "C6FZ7"
    assert parsed["draft_m"] == 7.2
    assert parsed["destination"] == "PHILIPSBURG"
    assert abs(parsed["lat"] - 18.0132) < 0.01

    # Test fallback with no credentials set
    res = query_live_aishub_vessels()
    assert isinstance(res, list)


def test_parse_kpler_feature():
    # pyrefly: ignore [missing-import]
    from src.data.kpler_api import parse_kpler_feature, query_kpler_latest_vessels

    sample_feature = {
        "type": "Feature",
        "id": 6764564,
        "geometry": {
            "type": "Point",
            "coordinates": [-2.3567834, 58.7598532]
        },
        "properties": {
            "vesselUid": 16,
            "mmsi": 987654321,
            "imo": 9128520,
            "longitude": -2.3567834,
            "latitude": 58.7598532,
            "sog": 10.2,
            "cog": 165,
            "rot": -16,
            "heading": 308,
            "navStatus": 0,
            "vesselName": "AVEL VAD",
            "callsign": "FNALV",
            "flag": "FR",
            "vesselType": "Bulk Carrier",
            "dwt": 45262,
            "grt": 62780,
            "destination": "Houston",
            "eta": "2025-12-01T12:00:00Z",
            "draught": 8.5,
            "posDt": "2025-09-10T15:02:20Z"
        }
    }
    parsed = parse_kpler_feature(sample_feature)
    assert parsed["mmsi"] == 987654321
    assert parsed["imo"] == 9128520
    assert parsed["vessel_name"] == "AVEL VAD"
    assert parsed["dwt"] == 45262
    assert parsed["draft_m"] == 8.5
    assert parsed["vessel_type"] == "Bulk Carrier"
    assert parsed["lat"] == 58.75985
    assert parsed["sog_knots"] == 10.2

    # Test fallback with no credentials set
    kpler_res = query_kpler_latest_vessels()
    assert isinstance(kpler_res, list)
