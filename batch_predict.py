"""
Batch Prediction CLI for Planned Shipments.
Usage:
    python batch_predict.py --input data/example/planned_shipments.csv --output recommendations.csv
"""
import argparse
import logging
import pandas as pd
# pyrefly: ignore [missing-import]
from typing import List, Dict, Any

# pyrefly: ignore [missing-import]
from src.schemas.input import RecommendationRequest
# pyrefly: ignore [missing-import]
from src.services.recommendation_service import RecommendationService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def run_batch_inference(input_csv: str, output_csv: str) -> None:
    logging.info(f"Loading planned shipments from {input_csv}...")
    df_in = pd.read_csv(input_csv)
    
    rec_service = RecommendationService()
    results = []
    
    for idx, row in df_in.iterrows():
        shipment_id = row.get("shipment_id", f"SHIP_{idx+1}")
        orig = str(row["origin_port"])
        dest = str(row["destination_port"])
        cargo = str(row.get("cargo_type", "Coking Coal"))
        size = float(row.get("cargo_size_tons", 70000.0))
        ship_date = str(row.get("ship_date", ""))
        w_cost = float(row.get("weight_cost", 0.50))
        w_speed = float(row.get("weight_speed", 0.30))
        w_rel = float(row.get("weight_reliability", 0.20))
        top_n = int(row.get("top_n", 5))
        
        req = RecommendationRequest(
            origin_port=orig,
            destination_port=dest,
            cargo_type=cargo,
            cargo_size_tons=size,
            ship_date=ship_date if ship_date else None,
            weight_cost=w_cost,
            weight_speed=w_speed,
            weight_reliability=w_rel,
            top_n=top_n
        )
        
        logging.info(f"Processing Shipment {shipment_id}: {orig} -> {dest} ({size:,.0f} MT {cargo})")
        res = rec_service.generate_recommendations(req)
        
        for ship in res.recommendations:
            results.append({
                "shipment_id": shipment_id,
                "origin_port": res.origin_port,
                "destination_port": res.destination_port,
                "cargo_type": res.cargo_type,
                "cargo_size_tons": res.cargo_size_tons,
                "market_regime": res.market_regime,
                "freight_rate_p10_usd_ton": res.freight_low,
                "freight_rate_p50_usd_ton": res.freight_median,
                "freight_rate_p90_usd_ton": res.freight_high,
                "rank": ship.rank,
                "vessel_id": ship.vessel_id,
                "vessel_name": ship.vessel_name,
                "vessel_class": ship.vessel_class,
                "availability_status": ship.availability_status,
                "port_feasible": ship.port_feasible,
                "predicted_voyage_cost_p10_usd": ship.predicted_cost_low,
                "predicted_voyage_cost_p50_usd": ship.predicted_cost_median,
                "predicted_voyage_cost_p90_usd": ship.predicted_cost_high,
                "market_avg_cost_usd": ship.market_avg_cost,
                "savings_vs_market_pct": ship.savings_vs_market_pct,
                "estimated_transit_days": ship.estimated_transit_days,
                "probability_on_time": ship.probability_on_time,
                "multi_objective_score": ship.multi_objective_score,
                "decision": ship.decision,
                "exclusion_or_risk_flags": "; ".join(ship.exclusion_or_risk_flags)
            })
            
    df_out = pd.DataFrame(results)
    df_out.to_csv(output_csv, index=False)
    logging.info(f"Batch prediction complete. Exported {len(df_out)} recommendation rows to {output_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run batch freight and vessel recommendations.")
    parser.add_argument("--input", required=True, help="Path to input shipments CSV")
    parser.add_argument("--output", default="recommendations.csv", help="Path to output recommendations CSV")
    args = parser.parse_args()
    
    run_batch_inference(args.input, args.output)
