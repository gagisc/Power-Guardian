"""LSTM-based sequence anomaly detector for power time-series.

Architecture stub — replace encoder body and adjust hyperparameters.
"""

from __future__ import annotations

import torch
import torch.nn as nn


class PowerLSTM(nn.Module):
    """Seq2Seq LSTM autoencoder for multivariate PDU timeseries.

    Parameters
    ----------
    n_features   : Number of input features (e.g. 8 power metrics).
    hidden_dim   : LSTM hidden state dimension.
    latent_dim   : Bottleneck size.
    n_layers     : Number of LSTM layers.
    seq_len      : Input sequence length (timesteps).
    """

    def __init__(
        self,
        n_features: int = 8,
        hidden_dim: int = 64,
        latent_dim: int = 16,
        n_layers: int = 2,
        seq_len: int = 32,
    ) -> None:
        super().__init__()
        self.seq_len = seq_len
        self.encoder = nn.LSTM(
            input_size=n_features,
            hidden_size=hidden_dim,
            num_layers=n_layers,
            batch_first=True,
        )
        self.latent = nn.Linear(hidden_dim, latent_dim)
        self.expand = nn.Linear(latent_dim, hidden_dim)
        self.decoder = nn.LSTM(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=n_layers,
            batch_first=True,
        )
        self.output_layer = nn.Linear(hidden_dim, n_features)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len, n_features)
        _, (h, _) = self.encoder(x)
        z = self.latent(h[-1])  # (batch, latent_dim)
        expanded = self.expand(z).unsqueeze(1).repeat(1, self.seq_len, 1)
        out, _ = self.decoder(expanded)
        return self.output_layer(out)  # (batch, seq_len, n_features)


class SequenceAnomalyDetector:
    def __init__(self, n_features: int = 8, seq_len: int = 32, threshold: float = 0.05) -> None:
        self.model = PowerLSTM(n_features=n_features, seq_len=seq_len)
        self.model.eval()
        self.threshold = threshold

    def score(self, window: torch.Tensor) -> float:
        with torch.no_grad():
            recon = self.model(window)
        return float(nn.functional.mse_loss(recon, window).item())

    def predict(self, window: torch.Tensor) -> bool:
        return self.score(window) > self.threshold
