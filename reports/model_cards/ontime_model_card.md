# Model Card: On-Time Arrival Probability Classifier

## Model Overview
- **Model Name:** Schedule Reliability Classifier (`lightgbm_ontime_v1`)
- **Version:** 1.0.0
- **Model Type:** Probability-Calibrated LightGBM Binary Classifier (via Platt Scaling / Isotonic Calibration)
- **Target Variable:** `on_time_flag` ($\in \{0, 1\}$, 1 = arrived within laycan schedule buffer)
- **Objective:** Binary cross-entropy minimizing log-loss and maximizing calibration quality

## Intended Use
- Predict the conditional probability $P(\text{on-time arrival} \mid \text{route, vessel, congestion, season})$.
- Feed reliability scores directly into the multi-objective vessel ranking function.
- Flag high-risk shipments subject to severe laytime / demurrage penalties.

## Key Features
- Derived destination port congestion index (`derived_congestion_index`)
- Estimated pre-berthing waiting days (`est_waiting_days`)
- Approaching vessel count and anchorage vessel count
- Route distance and vessel design speed
- Monsoon and seasonal weather flags

## Calibration & Performance Metrics
- **ROC-AUC & PR-AUC:** Discrimination ability
- **Brier Score:** Mean squared probability error (Target $\le 0.20$)
- **Expected Calibration Error (ECE):** Evaluated across 10 deciles of predicted probabilities
- **Reliability Diagram:** Visual alignment between predicted confidence and observed empirical positive rate
