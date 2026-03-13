"""
Transformer-based stock prediction model
Uses time-series transformer architecture for pattern recognition
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
from typing import List, Optional
import warnings

warnings.filterwarnings('ignore')


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer"""

    def __init__(self, d_model: int, max_len: int = 5000):
        super().__init__()
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))
        pe = torch.zeros(max_len, d_model)
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:x.size(1)]


class StockTransformer(nn.Module):
    """Transformer model for stock prediction"""

    def __init__(self, input_size: int = 8, d_model: int = 128, nhead: int = 8,
                 num_layers: int = 4, dropout: float = 0.1):
        super().__init__()

        self.input_projection = nn.Linear(input_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model, nhead, dim_feedforward=512, dropout=dropout, batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)

        self.decoder = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 3)  # buy, sell, hold
        )

        self.softmax = nn.Softmax(dim=-1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Project input
        x = self.input_projection(x)

        # Add positional encoding
        x = self.pos_encoder(x)

        # Transformer encoding
        x = self.transformer(x)

        # Global average pooling
        x = x.mean(dim=1)

        # Decode
        x = self.decoder(x)
        return self.softmax(x)


class TransformerPredictor:
    """Transformer-based stock predictor with advanced features"""

    def __init__(self, sequence_length: int = 30, device: str = None):
        self.sequence_length = sequence_length
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = StockTransformer(input_size=8).to(self.device)
        self.model.eval()

    def calculate_features(self, prices: List[float], volumes: List[int]) -> np.ndarray:
        """Calculate comprehensive technical indicators"""
        n = len(prices)
        features = np.zeros((n, 8))

        # Basic
        features[:, 0] = prices  # Close
        features[:, 1] = volumes  # Volume

        # Moving averages
        for i in range(n):
            if i >= 5:
                features[i, 2] = np.mean(prices[i-4:i+1])
            if i >= 20:
                features[i, 3] = np.mean(prices[i-19:i+1])
            if i >= 50:
                features[i, 4] = np.mean(prices[i-49:i+1])

        # Momentum
        for i in range(1, n):
            features[i, 5] = (prices[i] - prices[i-1]) / prices[i-1] * 100 if prices[i-1] > 0 else 0

        # Volatility
        for i in range(10, n):
            features[i, 6] = np.std(prices[i-9:i+1])

        # Volume ratio
        for i in range(10, n):
            features[i, 7] = volumes[i] / np.mean(volumes[i-9:i+1]) if np.mean(volumes[i-9:i+1]) > 0 else 1

        # Fill NaN values
        features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)

        return features

    def prepare_input(self, prices: List[float], volumes: List[int]) -> torch.Tensor:
        """Prepare transformer input"""
        features = self.calculate_features(prices, volumes)

        # Normalize
        means = np.mean(features, axis=0)
        stds = np.std(features, axis=0)
        stds[stds == 0] = 1
        normalized = (features - means) / stds

        # Truncate or pad
        if len(normalized) >= self.sequence_length:
            seq = normalized[-self.sequence_length:]
        else:
            pad = np.zeros((self.sequence_length - len(normalized), 8))
            seq = np.vstack([pad, normalized])

        return torch.FloatTensor(seq).unsqueeze(0).to(self.device)

    def predict(self, prices: List[float], volumes: List[int]) -> dict:
        """Predict using transformer model"""
        with torch.no_grad():
            x = self.prepare_input(prices, volumes)
            output = self.model(x)

        probs = output.cpu().numpy()[0]
        actions = ['hold', 'buy', 'sell']
        action_idx = np.argmax(probs)

        return {
            'action': actions[action_idx],
            'probabilities': {
                'hold': float(probs[0]),
                'buy': float(probs[1]),
                'sell': float(probs[2])
            },
            'confidence': float(probs[action_idx]),
            'model': 'Transformer'
        }
