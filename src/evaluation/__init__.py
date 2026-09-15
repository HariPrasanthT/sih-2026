"""
Model Evaluation, Metric Calculations, Calibration Audits, and Model Card Generation.
"""
# pyrefly: ignore [missing-import]
from src.evaluation.freight_metrics import (
    calculate_mape,
    calculate_smape,
    calculate_pinball_loss,
    evaluate_freight_predictions,
    evaluate_transit_predictions,
    evaluate_ontime_predictions,
)
# pyrefly: ignore [missing-import]
from src.evaluation.calibration import compute_binary_calibration
# pyrefly: ignore [missing-import]
from src.evaluation.ranking_metrics import (
    compute_dcg_at_k,
    compute_ndcg_at_k,
    compute_precision_at_k,
)
# pyrefly: ignore [missing-import]
from src.evaluation.report import (
    generate_evaluation_figures,
    generate_evaluation_report,
)

__all__ = [
    "calculate_mape",
    "calculate_smape",
    "calculate_pinball_loss",
    "evaluate_freight_predictions",
    "evaluate_transit_predictions",
    "evaluate_ontime_predictions",
    "compute_binary_calibration",
    "compute_dcg_at_k",
    "compute_ndcg_at_k",
    "compute_precision_at_k",
    "generate_evaluation_figures",
    "generate_evaluation_report",
]
