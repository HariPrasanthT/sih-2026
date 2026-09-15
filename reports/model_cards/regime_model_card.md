# Model Card: Freight Market Regime Classifier (Gaussian HMM)

## Model Overview
- **Model Name:** Latent Freight Volatility Regime Classifier (`hmm_regime_v1`)
- **Version:** 1.0.0
- **Model Type:** Gaussian Hidden Markov Model (HMM) via `hmmlearn`
- **States:** 3 Latent Market Regimes:
  1. `LOW_VOLATILITY`: Stable market, minimal price swing risk.
  2. `NORMAL`: Balanced market conditions, standard seasonal variations.
  3. `HIGH_VOLATILITY`: Turbulent market, rapid spot spikes, high demurrage/bunker uncertainty.

## Intended Use
- Detect latent macroeconomic market phases to contextualize freight risk.
- Trigger defensive charter strategies (`WAIT` / `AVOID` or longer forward covers) during high-volatility regimes.
- Provide risk flags to procurement executives.

## Key Features
- Daily freight log returns
- Rolling 30-day freight standard deviation (volatility)
- Daily Baltic Dry Index change percentage
- Bunker fuel price returns

## Limitations Notice
The HMM does not predict spot freight price directly; it characterizes the latent statistical regime of market volatility and transition probabilities.
