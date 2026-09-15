"""
Unit tests for ranking evaluation metrics (NDCG, Precision@K, MRR, Spearman correlation).
"""
import pytest
# pyrefly: ignore [missing-import]
from src.evaluation.ranking_metrics import (
    compute_dcg_at_k,
    compute_ndcg_at_k,
    compute_precision_at_k,
    compute_mrr,
    compute_rank_correlations
)


def test_ndcg_at_k_perfect_ranking():
    relevance = [3.0, 2.0, 1.0, 0.0]
    predicted_order = [0, 1, 2, 3]  # Perfect order
    ndcg = compute_ndcg_at_k(relevance, predicted_order, k=4)
    assert ndcg == pytest.approx(1.0, rel=1e-3)


def test_ndcg_at_k_inverted_ranking():
    relevance = [3.0, 2.0, 1.0, 0.0]
    predicted_order = [3, 2, 1, 0]  # Completely reversed
    ndcg = compute_ndcg_at_k(relevance, predicted_order, k=4)
    assert ndcg < 0.70


def test_precision_at_k():
    mask = [True, True, False, True, False]
    p3 = compute_precision_at_k(mask, k=3)
    assert p3 == pytest.approx(2.0 / 3.0)
    p5 = compute_precision_at_k(mask, k=5)
    assert p5 == pytest.approx(3.0 / 5.0)


def test_mrr():
    ranks = [1, 2, 3]
    mrr = compute_mrr(ranks)
    assert mrr == pytest.approx((1.0 + 0.5 + 0.333333) / 3.0, rel=1e-3)


def test_rank_correlations():
    actual = [10.0, 20.0, 30.0, 40.0]
    predicted = [12.0, 19.0, 31.0, 42.0]
    corrs = compute_rank_correlations(actual, predicted)
    assert corrs["spearman_rho"] == pytest.approx(1.0)
    assert corrs["kendall_tau"] == pytest.approx(1.0)
