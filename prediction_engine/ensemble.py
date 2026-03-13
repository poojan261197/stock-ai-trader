"""
Ensemble Predictor that combines multiple models
Uses weighted voting from LSTM, Transformer, and traditional ML
"""
from __future__ import annotations

import numpy as np
from typing import List, Dict
from dataclasses import dataclass
import json
from pathlib import Path

from .lstm_model import LSTMPredictor
from .transformer_model import TransformerPredictor


@dataclass
class ModelPrediction:
    """Individual model prediction result"""
    model_name: str
    action: str
    confidence: float
    probabilities: Dict[str, float]
    weight: float


class EnsemblePredictor:
    """
    Ensemble of multiple prediction models
    Combines LSTM, Transformer, and traditional signals
    """

    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize ensemble with model weights
        Default weights: LSTM=0.4, Transformer=0.4, Technical=0.2
        """
        self.weights = weights or {
            'lstm': 0.4,
            'transformer': 0.4,
            'technical': 0.2
        }

        self.device = 'cuda' if self._check_cuda() else 'cpu'

        # Initialize models
        self.lstm = LSTMPredictor(device=self.device)
        self.transformer = TransformerPredictor(device=self.device)

        # Model performance tracking
        self.performance_history = []

    def _check_cuda(self) -> bool:
        """Check if CUDA is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False

    def technical_analysis(self, prices: List[float], volumes: List[int]) -> Dict:
        """
        Traditional technical analysis signals
        """
        n = len(prices)
        if n < 20:
            return {'action': 'hold', 'probabilities': {'hold': 1.0, 'buy': 0, 'sell': 0}}

        signals = []

        # Moving Average Crossover
        ma5 = np.mean(prices[-5:])
        ma20 = np.mean(prices[-20:])

        if ma5 > ma20:
            signals.append(('buy', 0.3))
        elif ma5 < ma20:
            signals.append(('sell', 0.3))
        else:
            signals.append(('hold', 0.2))

        # RSI calculation
        if n >= 14:
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            avg_gain = np.mean(gains[-14:])
            avg_loss = np.mean(losses[-14:])

            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

            if rsi < 30:
                signals.append(('buy', 0.4))  # Oversold
            elif rsi > 70:
                signals.append(('sell', 0.4))  # Overbought
            else:
                signals.append(('hold', 0.2))

        # Volume spike
        avg_volume = np.mean(volumes[-10:])
        if volumes[-1] > avg_volume * 1.5:
            if prices[-1] > prices[-2]:
                signals.append(('buy', 0.2))
            else:
                signals.append(('sell', 0.2))

        # Calculate probabilities
        probs = {'hold': 0.0, 'buy': 0.0, 'sell': 0.0}
        for action, weight in signals:
            probs[action] += weight

        # Normalize
        total = sum(probs.values())
        if total > 0:
            probs = {k: v / total for k, v in probs.items()}

        action = max(probs, key=probs.get)

        return {
            'action': action,
            'probabilities': probs,
            'confidence': probs[action]
        }

    def predict(self, prices: List[float], volumes: List[int]) -> Dict:
        """
        Get ensemble prediction from all models
        """
        predictions = []

        # LSTM prediction
        try:
            lstm_pred = self.lstm.predict(prices, volumes)
            predictions.append(ModelPrediction(
                model_name='LSTM',
                action=lstm_pred['action'],
                confidence=lstm_pred['confidence'],
                probabilities=lstm_pred['probabilities'],
                weight=self.weights['lstm']
            ))
        except Exception as e:
            print(f"LSTM prediction failed: {e}")

        # Transformer prediction
        try:
            trans_pred = self.transformer.predict(prices, volumes)
            predictions.append(ModelPrediction(
                model_name='Transformer',
                action=trans_pred['action'],
                confidence=trans_pred['confidence'],
                probabilities=trans_pred['probabilities'],
                weight=self.weights['transformer']
            ))
        except Exception as e:
            print(f"Transformer prediction failed: {e}")

        # Technical analysis
        try:
            tech_pred = self.technical_analysis(prices, volumes)
            predictions.append(ModelPrediction(
                model_name='Technical',
                action=tech_pred['action'],
                confidence=tech_pred['confidence'],
                probabilities=tech_pred['probabilities'],
                weight=self.weights['technical']
            ))
        except Exception as e:
            print(f"Technical analysis failed: {e}")

        # Ensemble voting
        ensemble_probs = {'hold': 0.0, 'buy': 0.0, 'sell': 0.0}

        for pred in predictions:
            for action, prob in pred.probabilities.items():
                ensemble_probs[action] += prob * pred.weight

        # Normalize
        total_weight = sum(self.weights.values())
        ensemble_probs = {k: v / total_weight for k, v in ensemble_probs.items()}

        final_action = max(ensemble_probs, key=ensemble_probs.get)
        confidence = ensemble_probs[final_action]

        # Calculate model agreement
        actions = [p.action for p in predictions]
        agreement = sum(1 for a in actions if a == final_action) / len(actions) if actions else 0

        return {
            'action': final_action,
            'confidence': confidence,
            'probabilities': ensemble_probs,
            'model_votes': {p.model_name: p.action for p in predictions},
            'individual_predictions': [
                {
                    'model': p.model_name,
                    'action': p.action,
                    'confidence': p.confidence,
                    'weight': p.weight
                } for p in predictions
            ],
            'agreement': agreement,
            'recommendation_score': self._calculate_score(final_action, confidence, ensemble_probs)
        }

    def _calculate_score(self, action: str, confidence: float, probs: Dict) -> float:
        """
        Calculate a recommendation score (0-100)
        Higher score = better buy opportunity
        """
        if action == 'buy':
            base_score = 60
            confidence_bonus = confidence * 40
            return min(100, base_score + confidence_bonus)
        elif action == 'sell':
            return confidence * 40  # 0-40 range for sell
        else:
            return 40 + confidence * 20  # 40-60 range for hold

    def update_weights(self, model_performance: Dict[str, float]):
        """
        Update model weights based on recent performance
        Better performing models get higher weights
        """
        total = sum(model_performance.values())
        if total > 0:
            self.weights = {k: v / total for k, v in model_performance.items()}

    def save_weights(self, path: Path = None):
        """Save current weights to file"""
        path = path or Path('model_weights.json')
        with open(path, 'w') as f:
            json.dump({
                'weights': self.weights,
                'performance_history': self.performance_history
            }, f, indent=2)

    def load_weights(self, path: Path = None):
        """Load weights from file"""
        path = path or Path('model_weights.json')
        if path.exists():
            with open(path) as f:
                data = json.load(f)
                self.weights = data.get('weights', self.weights)
                self.performance_history = data.get('performance_history', [])
