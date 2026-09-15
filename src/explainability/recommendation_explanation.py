"""
Recommendation Decision and Explainability Engine for Vessel Chartering.
Synthesizes SHAP drivers, market regime, port congestion, economics, and reliability
into explainable CHARTER, WAIT, or AVOID recommendations.
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class RecommendationExplainer:
    """
    Generates explainable, auditable decision rationale for chartering options.
    """
    def __init__(
        self,
        savings_threshold_charter_pct: float = 2.0,
        on_time_threshold_charter: float = 0.70,
        congestion_threshold_avoid: float = 0.80,
        on_time_threshold_avoid: float = 0.40
    ):
        self.savings_threshold = savings_threshold_charter_pct
        self.on_time_charter = on_time_threshold_charter
        self.congestion_avoid = congestion_threshold_avoid
        self.on_time_avoid = on_time_threshold_avoid

    def determine_decision(
        self,
        port_feasible: bool,
        savings_pct: float,
        prob_on_time: float,
        congestion_index: float,
        market_regime: str,
        exclusion_reasons: Optional[List[str]] = None
    ) -> Tuple[str, List[str]]:
        """
        Evaluate operational and economic parameters to classify decision:
        CHARTER, WAIT, or AVOID.
        """
        flags = []
        if exclusion_reasons:
            flags.extend(exclusion_reasons)

        if not port_feasible:
            flags.append("PHYSICAL_PORT_INCOMPATIBILITY")
            return "AVOID", flags

        # Congestion risk check
        if congestion_index >= self.congestion_avoid:
            flags.append(f"HIGH_PORT_CONGESTION_RISK (Index {congestion_index:.2f} >= {self.congestion_avoid:.2f})")

        # Reliability check
        if prob_on_time < self.on_time_avoid:
            flags.append(f"HIGH_DELAY_RISK (On-time probability {prob_on_time*100:.1f}% < {self.on_time_avoid*100:.1f}%)")

        # Market regime factor
        if market_regime == "HIGH_VOLATILITY":
            flags.append("MARKET_REGIME_HIGH_VOLATILITY")

        # Determine strategy
        if "PHYSICAL_PORT_INCOMPATIBILITY" in flags or prob_on_time < self.on_time_avoid:
            return "AVOID", flags

        if savings_pct >= self.savings_threshold and prob_on_time >= self.on_time_charter and congestion_index < self.congestion_avoid:
            return "CHARTER", flags

        if savings_pct < 0.0 or congestion_index >= self.congestion_avoid or market_regime in ["RISING", "HIGH_VOLATILITY"]:
            # If freight rate is above market or port is congested, recommending WAIT / negotiate
            return "WAIT", flags

        return "CHARTER", flags

    def generate_narrative(
        self,
        vessel_name: str,
        vessel_class: str,
        destination_port: str,
        decision: str,
        predicted_cost: float,
        market_avg_cost: float,
        savings_pct: float,
        transit_days: float,
        prob_on_time: float,
        market_regime: str,
        top_shap_features: Optional[List[Dict[str, Any]]] = None,
        risk_flags: Optional[List[str]] = None
    ) -> str:
        """
        Construct a transparent, explainable decision narrative for procurement officers.
        """
        lines = []
        lines.append(f"### Strategy Recommendation: {decision} ({vessel_name} - {vessel_class})")
        lines.append(f"- **Destination Port:** {destination_port}")
        lines.append(f"- **Predicted Total Cost:** ${predicted_cost:,.2f} USD (Market Avg: ${market_avg_cost:,.2f} USD)")

        if savings_pct >= 0:
            lines.append(f"- **Economic Advantage:** **+{savings_pct:.2f}% savings** (${market_avg_cost - predicted_cost:,.2f} USD below market median).")
        else:
            lines.append(f"- **Economic Disadvantage:** **{abs(savings_pct):.2f}% premium** (${predicted_cost - market_avg_cost:,.2f} USD above market median).")

        lines.append(f"- **Operational Profile:** Estimated {transit_days:.1f} transit days with **{prob_on_time * 100:.1f}% on-time probability**.")
        lines.append(f"- **Market Regime:** Classified as **{market_regime}**.")

        if top_shap_features:
            lines.append("\n**Key Predictive Cost Drivers (SHAP Analysis):**")
            for feat in top_shap_features[:4]:
                name = feat.get("feature", "unknown")
                impact = feat.get("impact", 0.0)
                direction = "increased" if impact > 0 else "reduced"
                lines.append(f"  - `{name}`: {direction} freight forecast by approximately ${abs(impact):.2f}/ton")

        if risk_flags:
            lines.append("\n**Identified Operational Flags:**")
            for rf in risk_flags:
                lines.append(f"  - ⚠️ {rf}")

        return "\n".join(lines)
