"""
Ranking and Recommendation Evaluation Metrics.
Evaluates multi-objective vessel candidate rankings using NDCG@K, Precision@K, MRR, and Rank Correlations.
"""
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from scipy.stats import spearmanr, kendalltau

logger = logging.getLogger(__name__)


def compute_dcg_at_k(relevance_scores: List[float], k: int = 5) -> float:
    """Compute Discounted Cumulative Gain at rank K."""
    relevance = np.asarray(relevance_scores, dtype=float)[:k]
    if relevance.size == 0:
        return 0.0
    discounts = np.log2(np.arange(len(relevance)) + 2)
    return float(np.sum((2.0 ** relevance - 1.0) / discounts))


def compute_ndcg_at_k(actual_relevance: List[float], predicted_ordering: List[int], k: int = 5) -> float:
    """
    Compute Normalized Discounted Cumulative Gain at rank K.
    """
    if not actual_relevance:
        return 0.0
    k = min(k, len(actual_relevance))
    
    # Relevance of items in predicted order
    pred_rel = [actual_relevance[i] for i in predicted_ordering[:k] if i < len(actual_relevance)]
    dcg = compute_dcg_at_k(pred_rel, k)
    
    # Ideal DCG
    ideal_rel = sorted(actual_relevance, reverse=True)[:k]
    idcg = compute_dcg_at_k(ideal_rel, k)
    
    if idcg <= 0.0:
        return 1.0 if dcg <= 0.0 else 0.0
    return float(dcg / idcg)


def compute_precision_at_k(relevant_items_mask: List[bool], k: int = 5) -> float:
    """Compute fraction of top-K recommendations that are truly relevant/feasible."""
    if not relevant_items_mask or k <= 0:
        return 0.0
    top_k = relevant_items_mask[:k]
    return float(sum(top_k) / len(top_k))


def compute_mrr(relevant_ranks: List[int]) -> float:
    """Compute Mean Reciprocal Rank given 1-based ranks of first relevant item."""
    if not relevant_ranks:
        return 0.0
    reciprocals = [1.0 / r for r in relevant_ranks if r > 0]
    return float(np.mean(reciprocals)) if reciprocals else 0.0


def compute_rank_correlations(actual_scores: List[float], predicted_scores: List[float]) -> Dict[str, float]:
    """Compute Spearman's rho and Kendall's tau correlation between predicted and ideal orderings."""
    if len(actual_scores) < 2 or len(predicted_scores) < 2:
        return {"spearman_rho": 1.0, "kendall_tau": 1.0}
        
    rho, _ = spearmanr(actual_scores, predicted_scores)
    tau, _ = kendalltau(actual_scores, predicted_scores)
    
    return {
        "spearman_rho": float(rho) if not np.isnan(rho) else 0.0,
        "kendall_tau": float(tau) if not np.isnan(tau) else 0.0
    }
