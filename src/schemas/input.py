"""
Pydantic Request Schemas for Recommendations and Prediction Queries.
"""
from typing import Optional, Any
from datetime import date
from pydantic import BaseModel, Field, model_validator


class RecommendationRequest(BaseModel):
    origin_port: str = Field(default="HAY_POINT", json_schema_extra={"example": "HAY_POINT"}, description="Origin load port name or UN/LOCODE")
    destination_port: str = Field(default="DHAMRA", json_schema_extra={"example": "DHAMRA"}, description="Destination Indian East Coast port")
    cargo_type: str = Field(default="Coking Coal", json_schema_extra={"example": "Coking Coal"}, description="Bulk commodity type")
    cargo_size_tons: float = Field(default=70000.0, gt=5000, le=300000, json_schema_extra={"example": 70000.0}, description="Cargo volume in metric tonnes")
    quantity_mt: Optional[float] = Field(default=None, description="Alias for cargo_size_tons")
    ship_date: Optional[str] = Field(default=None, json_schema_extra={"example": "2026-09-15"}, description="Target shipping / laycan date (YYYY-MM-DD)")
    laycan_start: Optional[str] = Field(default=None, description="Start date of laycan window")
    laycan_end: Optional[str] = Field(default=None, description="End date of laycan window")
    priority: Optional[str] = Field(default="Balanced", description="Optimization priority: Cost, Speed, Reliability, or Balanced")
    weight_cost: float = Field(default=0.50, ge=0.0, le=1.0, json_schema_extra={"example": 0.50}, description="Optimization weight for freight/voyage cost")
    weight_speed: float = Field(default=0.30, ge=0.0, le=1.0, json_schema_extra={"example": 0.30}, description="Optimization weight for voyage transit speed")
    weight_reliability: float = Field(default=0.20, ge=0.0, le=1.0, json_schema_extra={"example": 0.20}, description="Optimization weight for on-time probability")
    top_n: int = Field(default=5, ge=1, le=10, json_schema_extra={"example": 5}, description="Number of top feasible vessels to rank (up to 10)")

    @model_validator(mode="before")
    @classmethod
    def map_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Map quantity_mt -> cargo_size_tons
            if "quantity_mt" in data and data["quantity_mt"]:
                data.setdefault("cargo_size_tons", float(data["quantity_mt"]))
            elif "cargo_size_tons" in data and data["cargo_size_tons"]:
                data.setdefault("quantity_mt", float(data["cargo_size_tons"]))
            # Map laycan_start -> ship_date
            if "laycan_start" in data and data["laycan_start"] and not data.get("ship_date"):
                data["ship_date"] = data["laycan_start"]
            # Map priority -> weights
            pri = str(data.get("priority", "")).lower()
            if pri == "cost":
                data["weight_cost"] = 0.70
                data["weight_speed"] = 0.15
                data["weight_reliability"] = 0.15
            elif pri == "speed":
                data["weight_cost"] = 0.20
                data["weight_speed"] = 0.60
                data["weight_reliability"] = 0.20
            elif pri == "reliability":
                data["weight_cost"] = 0.20
                data["weight_speed"] = 0.20
                data["weight_reliability"] = 0.60
        return data


class BatchPredictionRequest(BaseModel):
    input_file_path: str = Field(..., description="Path to CSV file with planned shipments")
    output_file_path: str = Field(default="recommendations.csv", description="Path to export output CSV")


class FreightRatePredictRequest(BaseModel):
    forecast_date: Optional[str] = Field(default="2026-09-15", description="Prediction target date (YYYY-MM-DD)")
    route_origin: Optional[str] = Field(default="NEWCASTLE", description="Load port name")
    route_destination: Optional[str] = Field(default="PARADIP", description="Discharge port name")
    vessel_class: Optional[str] = Field(default="Panamax", description="Vessel class")
    cargo_type: Optional[str] = Field(default="Coal", description="Bulk cargo type")
    cargo_quantity_mt: Optional[float] = Field(default=80000.0, description="Cargo volume in metric tonnes")
    bunker_vlsfo_usd: Optional[float] = Field(default=580.0, description="VLSFO fuel price")
    bdi_index: Optional[float] = Field(default=1850.0, description="Baltic Dry Index")
