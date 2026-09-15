"""
Charter Recommendation Orchestration Service.
Orchestrates the complete decision pipeline: port constraint validation, probabilistic freight inference,
voyage economics, multi-objective ranking, what-if strategy classification, and SHAP explainability.
"""
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import pandas as pd

# pyrefly: ignore [missing-import]
from src.schemas.input import RecommendationRequest
# pyrefly: ignore [missing-import]
from src.schemas.output import FreightRecommendationResponse, ShipRecommendation
# pyrefly: ignore [missing-import]
from src.services.prediction_service import PredictionService
# pyrefly: ignore [missing-import]
from src.data.port_mapping import normalize_port_name, get_port_constraints
# pyrefly: ignore [missing-import]
from src.data.loaders import load_vessel_master
# pyrefly: ignore [missing-import]
from src.optimization.port_compatibility import filter_feasible_vessels
# pyrefly: ignore [missing-import]
from src.optimization.voyage_cost import compute_voyage_economics
# pyrefly: ignore [missing-import]
from src.optimization.ranking import rank_vessels
# pyrefly: ignore [missing-import]
from src.optimization.what_if import evaluate_charter_decision
# pyrefly: ignore [missing-import]
from src.explainability.shap_explainer import FreightSHAPExplainer

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    End-to-end recommendation service powering REST API and batch workflows.
    """
    def __init__(self, prediction_service: Optional[PredictionService] = None):
        self.pred_service = prediction_service or PredictionService()
        self.shap_explainer = None
        if self.pred_service.freight_model is not None:
            self.shap_explainer = FreightSHAPExplainer(
                self.pred_service.freight_model,
                self.pred_service.freight_model.feature_names
            )
            
    def generate_recommendations(self, req: RecommendationRequest) -> FreightRecommendationResponse:
        """
        Execute full vessel recommendation engine for a shipment query.
        """
        query_id = str(uuid.uuid4())[:8]
        now_utc = datetime.now(timezone.utc)
        
        # 1. Resolve canonical ports
        canon_orig = normalize_port_name(req.origin_port) or req.origin_port.upper()
        canon_dest = normalize_port_name(req.destination_port) or req.destination_port.upper()
        
        # Determine candidate vessel class based on cargo volume
        if req.cargo_size_tons >= 120000:
            target_vclass = "Capesize"
        elif req.cargo_size_tons >= 60000:
            target_vclass = "Panamax"
        elif req.cargo_size_tons >= 35000:
            target_vclass = "Supramax"
        else:
            target_vclass = "Handysize"
            
        # 2. Build runtime feature vector
        feat_df = self.pred_service.build_inference_feature_vector(
            origin_port=canon_orig,
            destination_port=canon_dest,
            cargo_type=req.cargo_type,
            vessel_class=target_vclass,
            ship_date=req.ship_date
        )
        
        # 3. Model predictions
        freight_preds = self.pred_service.predict_freight(feat_df)
        market_regime = self.pred_service.detect_market_regime(feat_df)
        
        # 4. Load candidate vessels
        fleet_df = load_vessel_master()
        
        # 5. Filter vessels by port hard constraints
        feas_df, excl_df = filter_feasible_vessels(
            candidates_df=fleet_df,
            destination_port=canon_dest,
            cargo_size_tons=req.cargo_size_tons,
            cargo_type=req.cargo_type
        )
        
        if feas_df.empty:
            logger.warning(f"No feasible vessels found for {canon_dest} with cargo {req.cargo_size_tons} MT.")
            # Use candidate fallback for demonstration of exclusion reasons
            feas_df = fleet_df.head(req.top_n).copy()
            feas_df["port_feasible"] = False
            feas_df["exclusion_reasons"] = [["PORT_CONSTRAINT_ALL_CANDIDATES_EXCLUDED"]] * len(feas_df)
            
        # 6. Predict transit time and reliability per vessel
        transit_estimates = []
        ontime_estimates = []
        
        for _, v_row in feas_df.iterrows():
            v_feat = feat_df.copy()
            v_feat["dwt"] = v_row.get("dwt", 75000)
            v_feat["design_speed_knots"] = v_row.get("design_speed_knots", 14.0)
            t_days = self.pred_service.predict_transit_days(v_feat, speed_knots=v_row.get("design_speed_knots", 14.0))
            p_ontime = self.pred_service.predict_ontime_prob(v_feat)
            transit_estimates.append(t_days)
            ontime_estimates.append(p_ontime)
            
        feas_df["estimated_transit_days"] = transit_estimates
        feas_df["probability_on_time"] = ontime_estimates
        feas_df["derived_congestion_index"] = float(feat_df.get("derived_congestion_index", 0.4).iloc[0])
        
        # 7. Compute total voyage economics & savings relative to market
        costed_df = compute_voyage_economics(
            candidates_df=feas_df,
            freight_rate_p10=freight_preds["freight_low"],
            freight_rate_p50=freight_preds["freight_median"],
            freight_rate_p90=freight_preds["freight_high"],
            cargo_size_tons=req.cargo_size_tons,
            bunker_price_usd=620.0,
            est_waiting_days=float(feat_df.get("est_waiting_days", 2.0).iloc[0])
        )
        
        # 8. Multi-objective ranking
        ranked_df = rank_vessels(
            candidates_df=costed_df,
            weight_cost=req.weight_cost,
            weight_speed=req.weight_speed,
            weight_reliability=req.weight_reliability,
            top_n=req.top_n
        )
        
        # 9. Strategic Decisions (CHARTER / WAIT / AVOID)
        rec_items: List[ShipRecommendation] = []
        for _, row in ranked_df.iterrows():
            row_dict = row.to_dict()
            decision, flags = evaluate_charter_decision(row_dict, market_regime=market_regime)
            
            rec_items.append(ShipRecommendation(
                vessel_id=str(row_dict.get("vessel_id", "VSL_UNKNOWN")),
                vessel_name=str(row_dict.get("vessel_name", "Unknown")),
                predicted_cost_low=float(row_dict.get("predicted_cost_low", 0.0)),
                predicted_cost_median=float(row_dict.get("predicted_cost_median", 0.0)),
                predicted_cost_high=float(row_dict.get("predicted_cost_high", 0.0)),
                market_avg_cost=float(row_dict.get("market_avg_cost", 0.0)),
                savings_vs_market_pct=float(row_dict.get("savings_vs_market_pct", 0.0)),
                estimated_transit_days=float(row_dict.get("estimated_transit_days", 14.0)),
                probability_on_time=float(row_dict.get("probability_on_time", 0.85)),
                availability_status=str(row_dict.get("status", "available")),
                vessel_class=str(row_dict.get("vessel_class", "Panamax")),
                port_feasible=bool(row_dict.get("port_feasible", True)),
                multi_objective_score=float(row_dict.get("multi_objective_score", 0.85)),
                rank=int(row_dict.get("rank", 1)),
                decision=decision,
                exclusion_or_risk_flags=flags
            ))
            
        # 10. SHAP explanation
        shap_info = None
        if self.shap_explainer is not None:
            shap_info = self.shap_explainer.explain_instance(feat_df)
            
        return FreightRecommendationResponse(
            query_id=query_id,
            generated_at=now_utc,
            origin_port=canon_orig,
            destination_port=canon_dest,
            cargo_type=req.cargo_type,
            cargo_size_tons=req.cargo_size_tons,
            market_regime=market_regime,
            freight_low=freight_preds["freight_low"],
            freight_median=freight_preds["freight_median"],
            freight_high=freight_preds["freight_high"],
            recommendations=rec_items,
            weights_used={
                "weight_cost": req.weight_cost,
                "weight_speed": req.weight_speed,
                "weight_reliability": req.weight_reliability
            },
            model_version=self.pred_service.registry_info.get("freight_champion", "xgboost_quantile_v1"),
            data_freshness={
                "port_data_updated": "2026-09-02",
                "market_data_updated": "2026-09-02",
                "vessel_status_updated": "2026-09-02"
            },
            shap_explanation=shap_info
        )
