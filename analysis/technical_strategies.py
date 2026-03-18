"""
Technical Analysis Strategies Module
Momentum, Mean Reversion, Breakout, and Trend Following strategies
"""

import numpy as np
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class StrategyResult:
    """Result from a strategy analysis"""
    id: str
    name: str
    action: str  # buy, sell, hold
    confidence: float
    signal_strength: float
    metadata: Dict


class MultiStrategyAnalyzer:
    """Analyzes multiple trading strategies for a stock"""

    def __init__(self):
        self.strategies = {
            'momentum': self.momentum_strategy,
            'mean_reversion': self.mean_reversion_strategy,
            'breakout': self.breakout_strategy,
            'trend_following': self.trend_following_strategy,
            'volume_confirms': self.volume_confirmation_strategy
        }

    def analyze(self, symbol: str, current_price: float, prices: List[float],
                highs: List[float], lows: List[float], volumes: List[float]) -> StrategyResult:
        """Run all strategies and return combined result"""
        results = []

        for name, strategy in self.strategies.items():
            try:
                result = strategy(prices, highs, lows, volumes, current_price)
                results.append(result)
            except Exception as e:
                print(f"Strategy {name} failed: {e}")

        if not results:
            return StrategyResult(
                id='neutral',
                name='Neutral',
                action='hold',
                confidence=0,
                signal_strength=0,
                metadata={}
            )

        # Combine results
        buy_votes = sum(1 for r in results if r.action == 'buy')
        sell_votes = sum(1 for r in results if r.action == 'sell')

        if buy_votes > sell_votes and buy_votes >= 2:
            action = 'buy'
            confidence = np.mean([r.confidence for r in results if r.action == 'buy'])
        elif sell_votes > buy_votes and sell_votes >= 2:
            action = 'sell'
            confidence = np.mean([r.confidence for r in results if r.action == 'sell'])
        else:
            action = 'hold'
            confidence = 50

        return StrategyResult(
            id='combined',
            name='Multi-Strategy Ensemble',
            action=action,
            confidence=min(100, confidence),
            signal_strength=abs(buy_votes - sell_votes),
            metadata={'votes_buy': buy_votes, 'votes_sell': sell_votes}
        )

    def momentum_strategy(self, prices: List[float], highs: List[float],
                          lows: List[float], volumes: List[float],
                          current_price: float) -> StrategyResult:
        """Price momentum strategy"""
        if len(prices) < 20:
            return StrategyResult('momentum', 'Momentum', 'hold', 0, 0, {})

        # Calculate 20-day vs 50-day momentum
        price_20 = np.mean(prices[-20:])
        price_50 = np.mean(prices[-50:]) if len(prices) >= 50 else np.mean(prices)

        momentum = (price_20 - price_50) / price_50 * 100

        action = 'buy' if momentum > 5 else 'sell' if momentum < -5 else 'hold'
        confidence = min(100, abs(momentum) * 5)

        return StrategyResult(
            id='momentum',
            name='Momentum Strategy',
            action=action,
            confidence=confidence,
            signal_strength=abs(momentum),
            metadata={'momentum_20d': momentum}
        )

    def mean_reversion_strategy(self, prices: List[float], highs: List[float],
                                lows: List[float], volumes: List[float],
                                current_price: float) -> StrategyResult:
        """Mean reversion - buy oversold, sell overbought"""
        if len(prices) < 20:
            return StrategyResult('mean_reversion', 'Mean Reversion', 'hold', 0, 0, {})

        ma_20 = np.mean(prices[-20:])
        std_20 = np.std(prices[-20:])

        z_score = (current_price - ma_20) / std_20 if std_20 > 0 else 0

        action = 'buy' if z_score < -2 else 'sell' if z_score > 2 else 'hold'
        confidence = min(100, abs(z_score) * 25)

        return StrategyResult(
            id='mean_reversion',
            name='Mean Reversion',
            action=action,
            confidence=confidence,
            signal_strength=abs(z_score),
            metadata={'z_score': z_score}
        )

    def breakout_strategy(self, prices: List[float], highs: List[float],
                          lows: List[float], volumes: List[float],
                          current_price: float) -> StrategyResult:
        """Breakout strategy - breaks resistance or support"""
        if len(prices) < 20:
            return StrategyResult('breakout', 'Breakout', 'hold', 0, 0, {})

        recent_high = max(prices[-20:-5])
        recent_low = min(prices[-20:-5])

        # Breakout conditions
        broke_resistance = current_price > recent_high * 1.02
        broke_support = current_price < recent_low * 0.98

        if broke_resistance:
            action = 'buy'
            confidence = 70
        elif broke_support:
            action = 'sell'
            confidence = 70
        else:
            action = 'hold'
            confidence = 50

        distance_to_break = min(
            abs(current_price - recent_high) / recent_high,
            abs(current_price - recent_low) / recent_low
        ) * 100

        return StrategyResult(
            id='breakout',
            name='Breakout Strategy',
            action=action,
            confidence=confidence,
            signal_strength=distance_to_break,
            metadata={
                'resistance': recent_high,
                'support': recent_low,
                'distance_to_break': distance_to_break
            }
        )

    def trend_following_strategy(self, prices: List[float], highs: List[float],
                                 lows: List[float], volumes: List[float],
                                 current_price: float) -> StrategyResult:
        """Trend following using moving averages"""
        if len(prices) < 50:
            return StrategyResult('trend', 'Trend Following', 'hold', 0, 0, {})

        sma_20 = np.mean(prices[-20:])
        sma_50 = np.mean(prices[-50:])

        # Golden cross (bullish) / Death cross (bearish)
        golden_cross = sma_20 > sma_50 * 1.02
        death_cross = sma_20 < sma_50 * 0.98

        if golden_cross:
            action = 'buy'
            confidence = 75
        elif death_cross:
            action = 'sell'
            confidence = 75
        else:
            action = 'hold'
            confidence = 50

        trend_strength = abs((sma_20 - sma_50) / sma_50 * 100)

        return StrategyResult(
            id='trend_following',
            name='Trend Following',
            action=action,
            confidence=confidence,
            signal_strength=trend_strength,
            metadata={
                'sma_20': sma_20,
                'sma_50': sma_50,
                'trend_strength': trend_strength
            }
        )

    def volume_confirmation_strategy(self, prices: List[float], highs: List[float],
                                   lows: List[float], volumes: List[float],
                                   current_price: float) -> StrategyResult:
        """Volume-based confirmation strategy"""
        if len(volumes) < 20:
            return StrategyResult('volume', 'Volume Confirmation', 'hold', 0, 0, {})

        avg_volume = np.mean(volumes[-20:])
        current_volume = volumes[-1]

        price_change = ((prices[-1] - prices[-2]) / prices[-2] * 100) if len(prices) > 1 else 0

        # Volume spike with price move
        volume_spike = current_volume > avg_volume * 1.5
        significant_move = abs(price_change) > 2

        if volume_spike and significant_move:
            action = 'buy' if price_change > 0 else 'sell'
            confidence = min(100, (current_volume / avg_volume) * 30)
        else:
            action = 'hold'
            confidence = 50

        return StrategyResult(
            id='volume_confirms',
            name='Volume Confirmation',
            action=action,
            confidence=confidence,
            signal_strength=current_volume / avg_volume if avg_volume > 0 else 0,
            metadata={
                'volume_ratio': current_volume / avg_volume if avg_volume > 0 else 0,
                'price_change_pct': price_change
            }
        )
