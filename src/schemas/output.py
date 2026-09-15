"""
Pydantic Output and Response Schemas matching SIH 26006 specification.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ShipRecommendation(BaseModel):
    vessel_id: str
    vessel_name: str
    predicted_cost_low: float = Field(..., description="P10 total voyage cost in USD")
    predicted_cost_median: float = Field(..., description="P50 median total voyage cost in USD")
    predicted_cost_high: float = Field(..., description="P90 total voyage cost in USD")
    market_avg_cost: float = Field(..., description="Average median voyage cost across all feasible vessels")
    savings_vs_market_pct: float = Field(..., description="Percentage savings relative to market average")
    estimated_transit_days: float = Field(..., description="Expected voyage transit duration in days")
    probability_on_time: float = Field(..., description="Calibrated probability of on-time cargo arrival [0, 1]")
    availability_status: str
    vessel_class: str
    port_feasible: bool = True
    multi_objective_score: float = Field(..., description="Composite multi-objective optimization score")
    rank: int = Field(..., description="Vessel recommendation rank (1 = best)")
    decision: str = Field(..., description="CHARTER, WAIT, or AVOID")
    exclusion_or_risk_flags: List[str] = Field(default_factory=list, description="Operational flags or exclusion reasons")


class FreightRecommendationResponse(BaseModel):
    query_id: str
    generated_at: datetime
    origin_port: str
    destination_port: str
    cargo_type: str
    cargo_size_tons: float
    market_regime: str = Field(..., description="Latent market state: LOW_VOLATILITY, NORMAL, HIGH_VOLATILITY")
    freight_low: float = Field(..., description="P10 route freight rate (USD/ton)")
    freight_median: float = Field(..., description="P50 median route freight rate (USD/ton)")
    freight_high: float = Field(..., description="P90 route freight rate (USD/ton)")
    recommendations: List[ShipRecommendation]
    weights_used: Dict[str, float]
    model_version: str
    data_freshness: Dict[str, Any]
    shap_explanation: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    status: str
    model_version: str
    training_date: str
    data_latest_date: str
    data_freshness: Dict[str, Any]
    model_status: Dict[str, str]


class ModelMetricsResponse(BaseModel):
    freight_champion: str
    metrics: Dict[str, Any]
    transit_metrics: Dict[str, Any]
    ontime_metrics: Dict[str, Any]
    conformal_coverage: Dict[str, Any]


class PortConstraintsResponse(BaseModel):
    port_code: str
    port_name: str
    coast: str
    max_draft_m: float
    max_loa_m: float
    max_beam_m: float
    max_dwt_tonnes: float
    allowed_vessel_classes: List[str]
    avg_turnaround_days: float
