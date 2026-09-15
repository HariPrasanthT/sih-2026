"""
Market Regime Classification Engine.
Models latent freight market states (LOW_VOLATILITY, NORMAL, HIGH_VOLATILITY)
using Gaussian Hidden Markov / Gaussian Mixture Transition Dynamics.
"""
import logging
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
import joblib

logger = logging.getLogger(__name__)

REGIME_NAMES = {
    0: "LOW_VOLATILITY",
    1: "NORMAL",
    2: "HIGH_VOLATILITY"
}


class MarketRegimeHMM:
    """
    Gaussian Mixture & Transition Dynamic Model for latent freight market volatility regimes.
    """
    def __init__(self, n_states: int = 3, random_state: int = 42):
        self.n_states = n_states
        self.model = GaussianMixture(
            n_components=n_states,
            covariance_type="full",
            max_iter=150,
            random_state=random_state
        )
        self.regime_map: Dict[int, str] = {}
        self.transition_matrix: Optional[np.ndarray] = None
        self.name = "Gaussian_Regime_Model"
        
    def fit(self, returns_and_vol: np.ndarray) -> "MarketRegimeHMM":
        """
        Fit Gaussian Mixture on 2D array of [daily_returns, rolling_volatility]
        and compute state transition matrix.
        """
        if len(returns_and_vol.shape) == 1:
            returns_and_vol = returns_and_vol.reshape(-1, 1)
            
        clean_data = np.nan_to_num(returns_and_vol, nan=0.0, posinf=0.0, neginf=0.0)
        self.model.fit(clean_data)
        
        # Order states by mean variance / volatility
        if clean_data.shape[1] > 1:
            state_vols = [float(self.model.means_[i][1]) for i in range(self.n_states)]
        else:
            state_vols = [float(np.trace(self.model.covariances_[i])) for i in range(self.n_states)]
            
        sorted_indices = np.argsort(state_vols)
        
        self.regime_map = {
            int(sorted_indices[0]): "LOW_VOLATILITY",
            int(sorted_indices[1]): "NORMAL",
            int(sorted_indices[2]): "HIGH_VOLATILITY"
        }
        
        # Estimate empirical transition matrix
        state_seq = self.model.predict(clean_data)
        trans_counts = np.zeros((self.n_states, self.n_states))
        for t in range(len(state_seq) - 1):
            s_curr, s_next = state_seq[t], state_seq[t+1]
            trans_counts[s_curr, s_next] += 1
            
        row_sums = trans_counts.sum(axis=1, keepdims=True)
        self.transition_matrix = np.divide(trans_counts, np.maximum(row_sums, 1.0))
        
        logger.info(f"Market Regime Model fitted with {self.n_states} latent states.")
        return self
        
    def predict_regime(self, X: np.ndarray) -> List[str]:
        """Classify current regime label."""
        if len(X.shape) == 1:
            X = X.reshape(-1, 1)
        clean_data = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        state_seq = self.model.predict(clean_data)
        return [self.regime_map.get(int(s), "NORMAL") for s in state_seq]
        
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """State posterior probabilities."""
        if len(X.shape) == 1:
            X = X.reshape(-1, 1)
        clean_data = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        return self.model.predict_proba(clean_data)
        
    def save(self, filepath: str) -> None:
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            "model": self.model,
            "regime_map": self.regime_map,
            "n_states": self.n_states,
            "transition_matrix": self.transition_matrix
        }, filepath)
        
    @classmethod
    def load(cls, filepath: str) -> "MarketRegimeHMM":
        data = joblib.load(filepath)
        instance = cls(n_states=data["n_states"])
        instance.model = data["model"]
        instance.regime_map = data["regime_map"]
        instance.transition_matrix = data.get("transition_matrix")
        return instance
