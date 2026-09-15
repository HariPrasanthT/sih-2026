"""
Bulletproof API Verification Script for SAIL SIH 26006
Tests all 13 Backend API Endpoints with:
1. Live HTTP Mode (Zero dependencies, works in ANY Python using urllib)
2. In-Memory Mode (FastAPI TestClient fallback if server is not yet running)
3. Automatic sys.path setup to prevent ModuleNotFoundError
"""

import sys
import os
import json
import time
from pathlib import Path

# ── 1. Ensure Project Root is in sys.path ──────────────────────────────────────
possible_roots = [
    Path(__file__).resolve().parent,
    Path(r"e:\Sail_SIH"),
    Path.cwd()
]

project_root = None
for p in possible_roots:
    if (p / "src" / "api" / "app.py").exists():
        project_root = p
        break

if project_root and str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    os.chdir(str(project_root))

# ── 2. Endpoint Test Definitions ──────────────────────────────────────────────
ENDPOINTS = [
    ("GET", "/", None, "Root welcome & API metadata"),
    ("GET", "/health", None, "System health & model readiness"),
    ("GET", "/ports", None, "Indian East Coast port constraints"),
    ("GET", "/vessels", None, "Certified bulk carrier fleet"),
    ("GET", "/forecast?origin=Newcastle&destination=Paradip&days=30", None, "30-Day ML freight rate forecast"),
    ("POST", "/predict/freight-rate", {
        "forecast_date": "2026-09-15",
        "route_origin": "Newcastle",
        "route_destination": "Paradip",
        "vessel_class": "Panamax",
        "cargo_type": "Coal",
        "cargo_quantity_mt": 80000,
        "bunker_vlsfo_usd": 580.0,
        "bdi_index": 1850.0
    }, "Single-point multi-quantile prediction"),
    ("POST", "/recommendations", {
        "origin_port": "Newcastle",
        "destination_port": "Paradip",
        "quantity_mt": 80000,
        "cargo_type": "Coal",
        "laycan_start": "2026-09-10",
        "laycan_end": "2026-09-24",
        "priority": "Balanced",
        "contract_type": "Short-Term Multi-Voyage"
    }, "AI vessel charter ranking & recommendation"),
    ("GET", "/live/market", None, "Live macro indicators (BDI, Brent, FX)"),
    ("GET", "/live/weather", None, "Live marine weather & wave conditions"),
    ("GET", "/live/coal-dispatch", None, "Coal India dispatch telemetry"),
    ("GET", "/live/fleet", None, "Live fleet AIS position stream"),
    ("GET", "/model/metrics", None, "Model accuracy (RMSE, MAE, Conformal)"),
    ("GET", "/model/shap-features", None, "SHAP feature importance weights")
]

BASE_URL = "http://localhost:8000"

def is_server_running() -> bool:
    """Check if FastAPI server is live on port 8000 using standard library."""
    import urllib.request
    try:
        req = urllib.request.Request(f"{BASE_URL}/health", headers={"User-Agent": "HealthCheck"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return resp.status == 200
    except Exception:
        return False

def test_via_http():
    """Test all endpoints against live running server via urllib (zero extra dependencies)."""
    import urllib.request
    import urllib.error

    print("\n" + "=" * 75)
    print(f"  MODE: LIVE HTTP NETWORK CLIENT -> {BASE_URL}")
    print("=" * 75)

    passed_count = 0
    total_count = len(ENDPOINTS)

    for method, path, body, desc in ENDPOINTS:
        url = f"{BASE_URL}{path}"
        req = urllib.request.Request(url, method=method)
        req.add_header("User-Agent", "FreightIQ-Verifier")
        
        encoded_data = None
        if body is not None:
            req.add_header("Content-Type", "application/json")
            encoded_data = json.dumps(body).encode("utf-8")

        start_time = time.time()
        try:
            with urllib.request.urlopen(req, data=encoded_data, timeout=10) as resp:
                elapsed_ms = (time.time() - start_time) * 1000
                status_code = resp.status
                raw_body = resp.read().decode("utf-8", errors="replace")
                
                # Parse preview
                try:
                    data = json.loads(raw_body)
                    if isinstance(data, list):
                        preview = f"{len(data)} items returned"
                    elif isinstance(data, dict):
                        preview = f"Keys: {', '.join(list(data.keys())[:4])}"
                    else:
                        preview = str(data)[:40]
                except Exception:
                    preview = f"{len(raw_body)} bytes"

                if status_code == 200:
                    passed_count += 1
                    status_str = "\033[92m[ PASS ]\033[0m"
                else:
                    status_str = f"\033[91m[ {status_code} ]\033[0m"

                clean_path = path.split("?")[0]
                print(f" {status_str} {method:4s} {clean_path:24s} | {elapsed_ms:5.1f}ms | {preview}")

        except urllib.error.HTTPError as he:
            elapsed_ms = (time.time() - start_time) * 1000
            print(f" \033[91m[ FAIL ]\033[0m {method:4s} {path:24s} | HTTP {he.code}: {he.reason}")
        except Exception as exc:
            elapsed_ms = (time.time() - start_time) * 1000
            print(f" \033[91m[ ERR  ]\033[0m {method:4s} {path:24s} | {type(exc).__name__}: {exc}")

    print("=" * 75)
    pct = (passed_count / total_count) * 100
    if passed_count == total_count:
        print(f"\033[92m  VERIFICATION RESULT: ALL {total_count}/{total_count} ENDPOINTS PASSED ({pct:.0f}% SUCCESS)\033[0m")
    else:
        print(f"\033[91m  VERIFICATION RESULT: {passed_count}/{total_count} ENDPOINTS PASSED ({pct:.0f}%)\033[0m")
    print("=" * 75 + "\n")
    return passed_count == total_count

def test_via_testclient():
    """In-memory testing using FastAPI TestClient when port 8000 is not running."""
    print("\n" + "=" * 75)
    print("  MODE: IN-MEMORY FASTAPI TESTCLIENT (Server not detected on port 8000)")
    print("=" * 75)

    try:
        from fastapi.testclient import TestClient
        from src.api.app import app
    except ImportError as ie:
        print(f"\n[ERROR] Cannot import FastAPI / app: {ie}")
        print("Tip: Run `uvicorn src.api.app:app --port 8000` to start the live server first.\n")
        return False

    client = TestClient(app)
    passed_count = 0
    total_count = len(ENDPOINTS)

    for method, path, body, desc in ENDPOINTS:
        start_time = time.time()
        try:
            if method == "GET":
                res = client.get(path)
            else:
                res = client.post(path, json=body)

            elapsed_ms = (time.time() - start_time) * 1000
            status_code = res.status_code

            try:
                data = res.json()
                if isinstance(data, list):
                    preview = f"{len(data)} items returned"
                elif isinstance(data, dict):
                    preview = f"Keys: {', '.join(list(data.keys())[:4])}"
                else:
                    preview = str(data)[:40]
            except Exception:
                preview = f"{len(res.text)} bytes"

            if status_code == 200:
                passed_count += 1
                status_str = "\033[92m[ PASS ]\033[0m"
            else:
                status_str = f"\033[91m[ {status_code} ]\033[0m"

            clean_path = path.split("?")[0]
            print(f" {status_str} {method:4s} {clean_path:24s} | {elapsed_ms:5.1f}ms | {preview}")

        except Exception as exc:
            elapsed_ms = (time.time() - start_time) * 1000
            print(f" \033[91m[ ERR  ]\033[0m {method:4s} {path:24s} | {type(exc).__name__}: {exc}")

    print("=" * 75)
    pct = (passed_count / total_count) * 100
    if passed_count == total_count:
        print(f"\033[92m  VERIFICATION RESULT: ALL {total_count}/{total_count} ENDPOINTS PASSED ({pct:.0f}% SUCCESS)\033[0m")
    else:
        print(f"\033[91m  VERIFICATION RESULT: {passed_count}/{total_count} ENDPOINTS PASSED ({pct:.0f}%)\033[0m")
    print("=" * 75 + "\n")
    return passed_count == total_count

if __name__ == "__main__":
    if is_server_running():
        success = test_via_http()
    else:
        print("[INFO] No server responding at http://localhost:8000.")
        print("[INFO] Falling back to In-Memory FastAPI TestClient...")
        success = test_via_testclient()
    
    sys.exit(0 if success else 1)
