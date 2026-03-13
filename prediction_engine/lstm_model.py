"""
LSTM-based stock prediction model with attention mechanism
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
from typing import List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')


class AttentionLSTM(nn.Module):
    """LSTM with self-attention for time series prediction"""

    def __init__(self, input_size: int = 6, hidden_size: int = 128, num_layers: int = 3, dropout: float = 0.2):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # LSTM layers
        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers,
            batch_first=True, dropout=dropout if num_layers > 1 else 0
        )

        # Self-attention
        self.attention = nn.MultiheadAttention(hidden_size, num_heads=8, batch_first=True)

        # Fully connected layers
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 3)  # Output: buy, sell, hold probabilities
        )

        self.softmax = nn.Softmax(dim=-1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # LSTM forward
        lstm_out, _ = self.lstm(x)  # lstm_out: (batch, seq_len, hidden_size)

        # Self-attention
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)

        # Take the last time step
        out = attn_out[:, -1, :]

        # Fully connected
        out = self.fc(out)
        return self.softmax(out)


class LSTMPredictor:
    """LSTM-based stock predictor with technical indicators"""

    def __init__(self, sequence_length: int = 30, device: str = None):
        self.sequence_length = sequence_length
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = AttentionLSTM(input_size=6).to(self.device)
        self.model.eval()

    def calculate_technical_indicators(self, prices: List[float], volumes: List[int]) -> np.ndarray:
        """Calculate technical indicators for feature engineering"""
        n = len(prices)
        features = np.zeros((n, 6))

        # Basic features
        features[:, 0] = prices  # Close price
        features[:, 1] = volumes  # Volume

        # Moving averages
        for i in range(n):
            if i >= 5:
                features[i, 2] = np.mean(prices[i-4:i+1])  # 5-day SMA
            if i >= 20:
                features[i, 3] = np.mean(prices[i-19:i+1])  # 20-day SMA

        # Price momentum (returns)
        for i in range(1, n):
            features[i, 4] = (prices[i] - prices[i-1]) / prices[i-1] * 100 if prices[i-1] > 0 else 0

        # Volatility (rolling std)
        for i in range(5, n):
            features[i, 5] = np.std(prices[i-4:i+1])

        return features

    def prepare_sequence(self, prices: List[float], volumes: List[int]) -> torch.Tensor:
        """Prepare input sequence for LSTM"""
        features = self.calculate_technical_indicators(prices, volumes)

        # Normalize
        means = np.mean(features, axis=0)
        stds = np.std(features, axis=0)
        stds[stds == 0] = 1
        normalized = (features - means) / stds

        # Take last sequence_length days
        if len(normalized) >= self.sequence_length:
            seq = normalized[-self.sequence_length:]
        else:
            # Pad if not enough data
            pad = np.zeros((self.sequence_length - len(normalized), 6))
            seq = np.vstack([pad, normalized])

        return torch.FloatTensor(seq).unsqueeze(0).to(self.device)

    def predict(self, prices: List[float], volumes: List[int]) -> dict:
        """
        Predict action for given price/volume history
        Returns dict with probabilities and recommended action
        """
        with torch.no_grad():
            seq = self.prepare_sequence(prices, volumes)
            output = self.model(seq)

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
            'model': 'LSTM+Attention'
        }

    def train(self, price_history: List[List[float]], volume_history: List[List[int]],
              labels: List[int], epochs: int = 50):
        """Train the model on historical data (for future fine-tuning)"""
        self.model.train()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        criterion = nn.CrossEntropyLoss()

        for epoch in range(epochs):
            total_loss = 0
            for prices, volumes, label in zip(price_history, volume_history, labels):
                seq = self.prepare_sequence(prices, volumes)
                output = self.model(seq)

                target = torch.LongTensor([label]).to(self.device)
                loss = criterion(output, target)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch + 1}/{epochs}, Loss: {total_loss / len(price_history):.4f}")

        self.model.eval()
