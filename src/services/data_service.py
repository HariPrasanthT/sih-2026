"""
Data Service.
Provides query and retrieval interfaces for ports, vessels, manifest metadata, and quality reports.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
import pandas as pd

# pyrefly: ignore [missing-import]
from src.data.port_mapping import CANONICAL_PORTS
# pyrefly: ignore [missing-import]
from src.data.loaders import load_port_master, load_vessel_master
# pyrefly: ignore [missing-import]
from src.data.manifest import load_manifest

logger = logging.getLogger(__name__)


class DataService:
    """Service providing metadata and catalog queries."""
    
    @staticmethod
    def get_supported_ports() -> List[Dict[str, Any]]:
        """Return list of supported canonical Indian ports and their physical constraints."""
        ports = []
        for code, details in CANONICAL_PORTS.items():
            if details.get("coast") == "East Coast" or details.get("country") == "India":
                ports.append({
                    "port_code": code,
                    "port_name": code,
                    "country": details.get("country", "India"),
                    "coast": details.get("coast", "East Coast"),
                    "state": details.get("state", ""),
                    "max_draft_m": details.get("max_draft_m", 15.0),
                    "max_loa_m": details.get("max_loa_m", 280.0),
                    "max_beam_m": details.get("max_beam_m", 45.0),
                    "max_dwt_tonnes": details.get("max_dwt_tonnes", 100000),
                    "allowed_vessel_classes": details.get("allowed_vessel_classes", []),
                    "avg_turnaround_days": details.get("avg_turnaround_days", 3.0),
                })
        return ports
        
    @staticmethod
    def get_vessel_fleet(status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return registered vessels."""
        df = load_vessel_master()
        if status_filter:
            df = df[df["status"] == status_filter]
        return df.to_dict(orient="records")
        
    @staticmethod
    def get_manifest_metadata() -> Dict[str, Any]:
        """Return current data manifest."""
        return load_manifest()
