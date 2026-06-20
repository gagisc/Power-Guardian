"""IsolationForest anomaly detector for PDU power metrics."""

from __future__ import annotations

import numpy as np
from sklearn.ensemble import IsolationForest  # type: ignore


class PDUIsolationForest:
    """Thin sklearn IsolationForest wrapper with online partial-fit pattern.

    Parameters
    ----------
    contamination : float
        Expected fraction of anomalies (0–0.5).
    n_estimators  : int
        Number of trees.
    """

    def __init__(self, contamination: float = 0.05, n_estimators: int = 100) -> None:
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=42,
        )
        self._fitted = False

    def fit(self, X: np.ndarray) -> PDUIsolationForest:
        self.model.fit(X)
        self._fitted = True
        return self

    def score(self, X: np.ndarray) -> np.ndarray:
        """Return anomaly scores (lower = more anomalous)."""
        if not self._fitted:
            raise RuntimeError("Call fit() first.")
        return np.asarray(self.model.score_samples(X))

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Return 1 (normal) or -1 (anomaly)."""
        if not self._fitted:
            raise RuntimeError("Call fit() first.")
        return np.asarray(self.model.predict(X))
