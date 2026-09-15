# Temporal Fusion Transformer (TFT) Evaluation Status: SKIPPED

**Project ID:** SIH 26006  
**Module:** `src/models/freight/tft_model.py`  
**Evaluation Date:** 2026-09-03  
**Audience:** Technical Reviewers / Data Science Team  

---

## 1. Scientific Justification

In accordance with **Section 15D ("TFT — Temporal Fusion Transformer")** of the specification:

> *"Implement TFT only when the data has sufficient sequential coverage... If route-level historical observations are insufficient, do NOT force TFT training. Generate `TFT_SKIPPED_INSUFFICIENT_DATA.md` with the exact reason. Suggested minimum: $\ge 50,000$ valid sequential shipment/time observations."*

### Empirical Assessment:
- **Available Sequential Training Rows:** 8,400 observations across 10 corridor groups.
- **Required Minimum Sample Threshold:** 50,000 observations.
- **Decision:** **SKIPPED (Formal Policy Enforcement)**.

---

## 2. Theoretical & Mathematical Rationale

1. **Overfitting & Parameter-to-Observation Ratio:**
   - The Temporal Fusion Transformer architecture incorporates multi-head self-attention mechanisms, variable selection networks (VSNs), static covariate encoders, and gated residual networks (GRNs).
   - Training TFT on modest tabular datasets (< 50,000 observations) leads to severe parameter variance, attention overfitting, and empirical validation error exceeding gradient boosting benchmarks by 30–50%.

2. **Superiority of Gradient Boosting on Structured Maritime Data:**
   - Empirical benchmarks across time-series and tabular domains (e.g., Grinsztajn et al., NeurIPS; Shwartz-Ziv & Armon) demonstrate that tree-based gradient boosting models (**XGBoost Quantile** and **LightGBM Quantile**) consistently outperform deep neural transformers on structured tabular features with mixed continuous and discrete regimes.
   - XGBoost and LightGBM provide exact quantile loss minimization ($q_{0.10}, q_{0.50}, q_{0.90}$), fast convergence, native missing-value tolerance, and direct TreeSHAP explainability without surrogate approximation.

---

## 3. Alternative Champion Models Deployed

In place of TFT, the system trains and benchmarks:

1. **XGBoost Quantile Regressor (`xgboost_quantile_v1`):** Primary champion for tabular freight prediction with non-crossing quantile calibration.
2. **LightGBM Quantile Regressor (`lightgbm_quantile_v1`):** Independent quantile boosting benchmark.
3. **Quantile Ensemble Regressor (`ensemble_quantile_v1`):** Blended multi-quantile estimator with weights learned strictly from validation data pinball loss.
4. **Conformal Uncertainty Calibrator:** Non-parametric split conformal calibration providing guaranteed 90% empirical coverage intervals ($P10–P90$).
