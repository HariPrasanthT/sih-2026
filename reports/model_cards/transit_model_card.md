# Model Card: Voyage Transit Duration Estimator

## Model Overview
- **Model Name:** Voyage Transit Duration Regressor (`lightgbm_transit_v1`)
- **Version:** 1.0.0
- **Model Type:** LightGBM Gradient Boosted Regressor
- **Target Variable:** `transit_days` (Days from load port departure to discharge port arrival)
- **Objective:** Regression minimizing Mean Squared Error / Huber Loss

## Intended Use
- Predict anticipated sea voyage transit times for specific vessel class and corridor pairings.
- Provide transit duration estimates to calculate bunker consumption and vessel daily hire costs.
- Inform multi-objective ranking where transit speed is prioritized.

## Key Features
- Route nautical distance (`route_distance_nm`) including strait routing factors
- Vessel design service speed (`speed_knots`)
- Vessel class category (Capesize, Panamax, Supramax, Handysize)
- Destination port waiting pressure (`est_waiting_days`)
- Seasonal weather and monsoon indicator (`is_monsoon`)
- Vessel deadweight tonnage (`dwt`)

## Performance Metrics
- **MAE:** Target $\le 2.0$ days
- **RMSE:** Monitored on held-out test data
- **R² Score:** Assessed across major dry bulk routes
