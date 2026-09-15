# Model Card: Freight Rate Forecasting Engine (XGBoost Quantile & Ensemble)

## Model Overview
- **Model Name:** Multi-Quantile Freight Rate Regressor (`xgboost_quantile_v1` / `ensemble_quantile_v1`)
- **Version:** 1.0.0
- **Model Type:** Gradient Boosted Decision Trees (XGBoost / LightGBM) with Quantile Pinball Loss
- **Quantiles Output:** $q_{0.10}$ (P10 - optimistic/low cost), $q_{0.50}$ (P50 - median forecast), $q_{0.90}$ (P90 - conservative/high cost)
- **Target Variable:** `freight_usd_per_ton` (USD per metric tonne)
- **Domain:** Inbound overseas dry bulk shipping to Indian East Coast ports (Paradip, Dhamra, Visakhapatnam, Gangavaram, Kamarajar, Haldia)

## Intended Use
- Forecast expected voyage charter freight rates for planned bulk procurement shipments.
- Provide probabilistic uncertainty intervals for risk-adjusted chartering decisions.
- Inform multi-objective vessel ranking and charter timing strategies.

## Inputs and Features
1. **Freight Momentum & Lags:** `freight_lag_1d`, `freight_lag_3d`, `freight_lag_7d`, `freight_lag_14d`, `freight_lag_30d`
2. **Rolling Statistics:** 7-day, 30-day, and 90-day rolling means and standard deviations
3. **Route Geography:** Great-circle nautical miles (`route_distance_nm`), load/discharge port pair
4. **Market & Fuel Benchmarks:** Baltic Dry Index (`bdi_index`), Very Low Sulfur Fuel Oil (`bunker_vlsfo_usd_ton`), USD/INR exchange rate (`usd_inr_rate`)
5. **Port Operations & Congestion:** `derived_congestion_index`, `est_waiting_days`, anchorage vessel density
6. **Seasonality:** Cyclic month and day-of-week transforms, Indian monsoon indicator (`is_monsoon`: June–Sept)

## Training & Validation Methodology
- **Split Strategy:** Strict chronological partition (70% train, 15% validation, 15% held-out test). Zero temporal shuffling or forward-looking leakage.
- **Quantile Calibration:** Enforced non-crossing post-processing: $P10 \le P50 \le P90$.
- **Uncertainty Calibration:** Calibrated via non-parametric split conformal prediction to achieve target 90% empirical coverage (PICP).

## Performance Metrics (Held-Out Test Set)
- **MAE:** Calculated from test set ($/ton)
- **RMSE:** Calculated from test set ($/ton)
- **MAPE / SMAPE:** Evaluated against baseline benchmarks
- **Pinball Losses:** Evaluated at $\alpha \in \{0.10, 0.50, 0.90\}$
- **Prediction Interval Coverage (PICP):** Evaluated against nominal 90% target (Acceptable band: 85%–95%)

## Ethical & Anti-Fabrication Notice
All metrics are derived strictly from validation/test data. In the absence of commercial proprietary fixtures, tests utilize the isolated development partition with complete transparency.
