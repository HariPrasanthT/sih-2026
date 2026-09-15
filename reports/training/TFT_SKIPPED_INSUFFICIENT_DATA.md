# Temporal Fusion Transformer (TFT) Evaluation Status: SKIPPED

## Scientific Justification
**Reason:** Insufficient sequential observations for deep multi-horizon attention modeling.

- **Available Training Observations:** 8,400
- **Required Minimum Threshold:** 50,000
- **Decision:** Skipped in favor of Tree-Based Gradient Boosting (XGBoost / LightGBM) to prevent high-variance overfitting and excessive parameter estimation error.

## Architectural Policy
Gradient boosting (XGBoost / LightGBM) is the mathematically superior and empirically robust choice for modest structured tabular maritime data. Deep neural multi-horizon networks like TFT require high-frequency multi-year continuous observations across dozens of concurrent entity series.
