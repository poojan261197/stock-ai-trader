"""
Advanced Trading Strategies Module
Additional strategies: Pairs Trading, Fibonacci, Bollinger Bands, etc.
"""
from __future__ import annotations

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class StrategyType(Enum):
    PAIRS_TRADING = "pairs_trading"
    BOLLINGER_SQUEEZE = "bollinger_squeeze"
    GOLDEN_CROSS = "golden_cross"
    RSI_DIVERGENCE = "rsi_divergence"
    MACD_CROSSOVER = "macd_crossover"
    ADX_TREND = "adx_trend"
    FIBONACCI_RETRACEMENT = "fibonacci_retracement"
    ICHIMOKU_CLOUD = "ichimoku_cloud"
    RELATIVE_STRENGTH = "relative_strength"
    VOLUME_PROFILE = "volume_profile"
    PARABOLIC_SAR = "parabolic_sar"
    STOCHASTIC_RSI = "stochastic_rsi"
    VWAP_DEVIATION = "vwap_deviation"
    DONCHIAN_CHANNEL = "donchian_channel"
    KELTNER_CHANNEL = "keltner_channel"


@dataclass
class StrategySignal:
    """Strategy signal with metadata"""
    strategy_name: str
    action: str  # buy, sell, hold
    confidence: float
    strength: float
    metadata: Dict
    price_target: Optional[float] = None
    stop_loss: Optional[float] = None


class AdvancedStrategyAnalyzer:
    """Advanced trading strategy analyzer"""

    def __init__(self):
        self.strategies = {
            StrategyType.BOLLINGER_SQUEEZE: self.bollinger_squeeze_strategy,
            StrategyType.GOLDEN_CROSS: self.golden_cross_strategy,
            StrategyType.RSI_DIVERGENCE: self.rsi_divergence_strategy,
            StrategyType.MACD_CROSSOVER: self.macd_crossover_strategy,
            StrategyType.ADX_TREND: self.adx_trend_strategy,
            StrategyType.FIBONACCI_RETRACEMENT: self.fibonacci_strategy,
            StrategyType.ICHIMOKU_CLOUD: self.ichimoku_strategy,
            StrategyType.PARABOLIC_SAR: self.parabolic_sar_strategy,
            StrategyType.STOCHASTIC_RSI: self.stochastic_rsi_strategy,
            StrategyType.VWAP_DEVIATION: self.vwap_deviation_strategy,
            StrategyType.DONCHIAN_CHANNEL: self.donchian_channel_strategy,
        }

    def analyze(self, symbol: str, prices: List[float], highs: List[float],
                lows: List[float], volumes: List[float]) -> List[StrategySignal]:
        """Run all advanced strategies"""
        signals = []
        for strategy_type, strategy_fn in self.strategies.items():
            try:
                signal = strategy_fn(prices, highs, lows, volumes)
                if signal:
                    signals.append(signal)
            except Exception as e:
                pass
        return signals

    def bollinger_squeeze_strategy(self, prices: List[float], highs: List[float],
                                    lows: List[float], volumes: List[float]) -> Optional[StrategySignal]:
        """Bollinger Band Squeeze - volatility breakout"""
        if len(prices) < 20:
            return None

        # Calculate Bollinger Bands
        ma_20 = np.mean(prices[-20:])
        std_20 = np.std(prices[-20:])

        upper_bb = ma_20 + 2 * std_20
        lower_bb = ma_20 - 2 * std_20
        current_price = prices[-1]

        # Calculate Band Width
        band_width = (upper_bb - lower_bb) / ma_20

        # Check for squeeze (band width narrows)
        if len(prices) >= 40:
            prev_ma = np.mean(prices[-40:-20])
            prev_std = np.std(prices[-40:-20])
            prev_width = (prev_ma + 2 * prev_std - (prev_ma - 2 * prev_std)) / prev_ma

            is_squeeze = band_width < prev_width * 0.8

            if is_squeeze:
                # Determine breakout direction
                direction = 'buy' if current_price > ma_20 else 'sell'
                confidence = 70 if band_width < 0.05 else 60

                return StrategySignal(
                    strategy_name='Bollinger_Squeeze',
                    action=direction,
                    confidence=confidence,
                    strength=band_width,
                    metadata={
                        'bb_upper': upper_bb,
                        'bb_lower': lower_bb,
                        'bb_middle': ma_20,
                        'squeeze_detected': True
                    },
                    price_target=current_price * (1.05 if direction == 'buy' else 0.95),
                    stop_loss=current_price * (0.97 if direction == 'buy' else 1.03)
                )

        return None

    def golden_cross_strategy(self, prices: List[float], highs: List[float],
                              lows: List[float], volumes: List[float]) -> Optional[StrategySignal]:
        """Golden Cross (50/200 MA) - long-term trend"""
        if len(prices) < 200:
            return None

        ma_50 = np.mean(prices[-50:])
        ma_200 = np.mean(prices[-200:])
        prev_ma_50 = np.mean(prices[-51:-1])
        prev_ma_200 = np.mean(prices[-201:-1])

        current_price = prices[-1]

        # Golden Cross: 50 MA crosses above 200 MA
        golden_cross = prev_ma_50 <= prev_ma_200 and ma_50 > ma_200
        death_cross = prev_ma_50 >= prev_ma_200 and ma_50 < ma_200

        if golden_cross:
            price_above_both = current_price > ma_50 and current_price > ma_200
            confidence = 85 if price_above_both else 75

            return StrategySignal(
                strategy_name='Golden_Cross',
                action='buy',
                confidence=confidence,
                strength=abs(ma_50 - ma_200) / ma_200 * 100,
                metadata={
                    'ma_50': ma_50,
                    'ma_200': ma_200,
                    'gap_percent': (current_price - ma_200) / ma_200 * 100,
                    'is_golden_cross': True
                }
            )

        if death_cross:
            return StrategySignal(
                strategy_name='Death_Cross',
                action='sell',
                confidence=80,
                strength=abs(ma_50 - ma_200) / ma_200 * 100,
                metadata={
                    'ma_50': ma_50,
                    'ma_200': ma_200,
                    'is_death_cross': True
                }
            )

        return None

    def rsi_divergence_strategy(self, prices: List[float], highs: List[float],
                                 lows: List[float], volumes: List[float]) -> Optional[StrategySignal]:
        """RSI Divergence - reversal pattern"""
        if len(prices) < 30:
            return None

        rsi = self._calculate_rsi(prices, 14)
        if len(rsi) < 15:
            return None

        # Check for bullish divergence (price lower low, RSI higher low)
        price_low_recent = min(prices[-7:])
        price_low_prev = min(prices[-14:-7])
        rsi_low_recent = min(rsi[-7:])
        rsi_low_prev = min(rsi[-14:-7])

        bullish_div = price_low_recent < price_low_prev and rsi_low_recent > rsi_low_prev

        # Check for bearish divergence
        price_high_recent = max(prices[-7:])
        price_high_prev = max(prices[-14:-7])
        rsi_high_recent = max(rsi[-7:])
        rsi_high_prev = max(rsi[-14:-7])

        bearish_div = price_high_recent > price_high_prev and rsi_high_recent < rsi_high_prev

        if bullish_div and rsi_low_recent < 40:
            return StrategySignal(
                strategy_name='RSI_Divergence_Bullish',
                action='buy',
                confidence=80,
                strength=abs(rsi_low_recent - rsi_low_prev),
                metadata={
                    'divergence_type': 'bullish',
                    'rsi_current': rsi[-1],
                    'price_low_recent': price_low_recent,
                    'price_low_prev': price_low_prev
                }
            )

        if bearish_div and rsi_high_recent > 60:
            return StrategySignal(
                strategy_name='RSI_Divergence_Bearish',
                action='sell',
                confidence=80,
                strength=abs(rsi_high_recent - rsi_high_prev),
                metadata={
                    'divergence_type': 'bearish',
                    'rsi_current': rsi[-1]
                }
            )

        return None

    def macd_crossover_strategy(self, prices: List[float], highs: List[float],
                                 lows: List[float], volumes: List[float]) -> Optional[StrategySignal]:
        """MACD Signal Line Crossover"""
        if len(prices) < 35:
            return None

        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)

        if len(ema_12) < 1 or len(ema_26) < 1:
            return None

        macd_line = [e12 - e26 for e12, e26 in zip(ema_12[-15:], ema_26[-15:])]
        signal_line = self._calculate_ema(macd_line, 9)

        if len(signal_line) < 2:
            return None

        # Check for crossover
        prev_macd = macd_line[-2]
        curr_macd = macd_line[-1]
        prev_signal = signal_line[-2]
        curr_signal = signal_line[-1]

        bullish_cross = prev_macd <= prev_signal and curr_macd > curr_signal
        bearish_cross = prev_macd >= prev_signal and curr_macd < curr_signal

        if bullish_cross and curr_macd > 0:
            return StrategySignal(
                strategy_name='MACD_Bullish',
                action='buy',
                confidence=75,
                strength=abs(curr_macd),
                metadata={
                    'macd_value': curr_macd,
                    'signal_value': curr_signal,
                    'histogram': curr_macd - curr_signal
                }
            )

        if bearish_cross and curr_macd < 0:
            return StrategySignal(
                strategy_name='MACD_Bearish',
                action='sell',
                confidence=75,
                strength=abs(curr_macd),
                metadata={
                    'macd_value': curr_macd,
                    'signal_value': curr_signal
                }
            )

        return None

    def adx_trend_strategy(self, prices: List[float], highs: List[float],
                           lows: List[float], volumes: List[float]) -> Optional[StrategySignal]:
        """ADX Trend Strength"""
        if len(prices) < 20:
            return None

        adx = self._calculate_adx(highs, lows, prices, 14)

        if adx is None:
            return None

        strength = adx

        if strength > 25:
            # Trend is strong
            direction = 'buy' if prices[-1] > np.mean(prices[-10:]) else 'sell'
            return StrategySignal(
                strategy_name='ADX_Strong_Trend',
                action=direction,
                confidence=min(85, strength),
                strength=strength,
                metadata={
                    'adx_value': adx,
                    'trend_strength': 'strong' if adx > 25 else 'moderate'
                }
            )

        return None

    def fibonacci_strategy(self, prices: List[float], highs: List[float],
                           lows: List[float], volumes: List[float]) -> Optional[StrategySignal]:
        """Fibonacci Retracement Levels"""
        if len(prices) < 50:
            return None

        # Find swing high and low
        recent_highs = [highs[-i] for i in range(1, 30)]
        recent_lows = [lows[-i] for i in range(1, 30)]

        swing_high = max(recent_highs)
        swing_low = min(recent_lows)
        current = prices[-1]

        # Calculate retracement levels
        diff = swing_high - swing_low
        levels = {
            '0.236': swing_high - 0.236 * diff,
            '0.382': swing_high - 0.382 * diff,
            '0.5': swing_high - 0.5 * diff,
            '0.618': swing_high - 0.618 * diff,
            '0.786': swing_high - 0.786 * diff
        }

        # Check proximity to a level
        for level, price_level in levels.items():
            if abs(current - price_level) / current < 0.01:
                # Near Fibonacci level
                if float(level) <= 0.5:
                    action = 'buy'  # Support
                else:
                    action = 'sell'  # Resistance

                return StrategySignal(
                    strategy_name=f'Fibonacci_{level}',
                    action=action,
                    confidence=70,
                    strength=float(level),
                    metadata={
                        'fib_level': level,
                        'fib_price': price_level,
                        'swing_high': swing_high,
                        'swing_low': swing_low
                    }
                )

        return None

    def ichimoku_strategy(self, prices: List[float], highs: List[float],
                          lows: List[float], volumes: List[float]) -> Optional[StrategySignal]:
        """Ichimoku Cloud Strategy"""
        if len(prices) < 52:
            return None

        # Tenkan-sen (Conversion line): (9-period high + 9-period low)/2
        tenkan = (max(highs[-9:]) + min(lows[-9:])) / 2

        # Kijun-sen (Base line): (26-period high + 26-period low)/2
        kijun = (max(highs[-26:]) + min(lows[-26:])) / 2

        # Senkou Span A: (Tenkan + Kijun) / 2
        senkou_a = (tenkan + kijun) / 2

        # Senkou Span B: (52-period high + 52-period low) / 2
        senkou_b = (max(highs[-52:]) + min(lows[-52:])) / 2

        current = prices[-1]

        # Price above cloud = bullish, below = bearish
        cloud_top = max(senkou_a, senkou_b)
        cloud_bottom = min(senkou_a, senkou_b)

        # TK cross
        bullish_tk = prices[-2] <= prices[-1] and tenkan > kijun and current > cloud_top
        bearish_tk = prices[-2] >= prices[-1] and tenkan < kijun and current < cloud_bottom

        if bullish_tk:
            return StrategySignal(
                strategy_name='Ichimoku_Bullish',
                action='buy',
                confidence=80,
                strength=abs(current - kijun) / current * 100,
                metadata={
                    'tenkan': tenkan,
                    'kijun': kijun,
                    'cloud_top': cloud_top,
                    'cloud_bottom': cloud_bottom
                }
            )

        if bearish_tk:
            return StrategySignal(
                strategy_name='Ichimoku_Bearish',
                action='sell',
                confidence=80,
                strength=abs(current - kijun) / current * 100,
                metadata={
                    'tenkan': tenkan,
                    'kijun': kijun
                }
            )

        return None

    def parabolic_sar_strategy(self, prices: List[float], highs: List[float],
                               lows: List[float], volumes: List[float]) -> Optional[StrategySignal]:
        """Parabolic SAR momentum"""
        if len(prices) < 20:
            return None

        # Simplified SAR calculation
        af = 0.02
        max_af = 0.2

        sar = lows[-2] if prices[-1] > prices[-2] else highs[-2]
        ep = highs[-2] if prices[-1] > prices[-2] else lows[-2]

        # Bullish: price above SAR
        # Bearish: price below SAR
        if prices[-1] > sar:
            return StrategySignal(
                strategy_name='Parabolic_SAR_Bullish',
                action='buy',
                confidence=70,
                strength=abs(prices[-1] - sar) / prices[-1] * 100,
                metadata={'sar_value': sar}
            )
        else:
            return StrategySignal(
                strategy_name='Parabolic_SAR_Bearish',
                action='sell',
                confidence=70,
                strength=abs(prices[-1] - sar) / prices[-1] * 100,
                metadata={'sar_value': sar}
            )

    def stochastic_rsi_strategy(self, prices: List[float], highs: List[float],
                                 lows: List[float], volumes: List[float]) -> Optional[StrategySignal]:
        """Stochastic RSI oversold/overbought"""
        if len(prices) < 20:
            return None

        rsi = self._calculate_rsi(prices, 14)
        if len(rsi) < 14:
            return None

        # Calculate Stochastic RSI
        rsi_min = min(rsi[-14:])
        rsi_max = max(rsi[-14:])

        if rsi_max == rsi_min:
            return None

        stoch_rsi = (rsi[-1] - rsi_min) / (rsi_max - rsi_min) * 100

        if stoch_rsi < 20:
            return StrategySignal(
                strategy_name='StochRSI_Oversold',
                action='buy',
                confidence=80 - stoch_rsi * 2,  # Higher confidence when more oversold
                strength=stoch_rsi,
                metadata={'stoch_rsi': stoch_rsi, 'rsi': rsi[-1]}
            )

        if stoch_rsi > 80:
            return StrategySignal(
                strategy_name='StochRSI_Overbought',
                action='sell',
                confidence=(stoch_rsi - 80) * 2 + 60,  # Higher confidence when more overbought
                strength=100 - stoch_rsi,
                metadata={'stoch_rsi': stoch_rsi, 'rsi': rsi[-1]}
            )

        return None

    def vwap_deviation_strategy(self, prices: List[float], highs: List[float],
                                 lows: List[float], volumes: List[float]) -> Optional[StrategySignal]:
        """VWAP Deviation - institutional benchmark"""
        if len(prices) < 20 or len(volumes) < 20:
            return None

        # Calculate VWAP over last 20 periods
        typical_prices = [(h + l + c) / 3 for h, l, c in zip(highs[-20:], lows[-20:], prices[-20:])]
        cumulative_tp_vol = sum(tp * vol for tp, vol in zip(typical_prices, volumes[-20:]))
        cumulative_vol = sum(volumes[-20:])

        if cumulative_vol == 0:
            return None

        vwap = cumulative_tp_vol / cumulative_vol
        current = prices[-1]
        deviation = (current - vwap) / vwap * 100

        if abs(deviation) > 2:
            # Significant deviation from VWAP
            action = 'buy' if deviation < -2 else 'sell'
            return StrategySignal(
                strategy_name='VWAP_Deviation',
                action=action,
                confidence=75,
                strength=abs(deviation),
                metadata={
                    'vwap': vwap,
                    'deviation_pct': deviation
                },
                price_target=vwap  # Mean reversion target
            )

        return None

    def donchian_channel_strategy(self, prices: List[float], highs: List[float],
                                 lows: List[float], volumes: List[float]) -> Optional[StrategySignal]:
        """Donchian Channel Breakout"""
        if len(prices) < 20:
            return None

        upper = max(highs[-20:])
        lower = min(lows[-20:])
        middle = (upper + lower) / 2
        current = prices[-1]

        # Breakout above channel
        if current > upper * 1.01 and prices[-2] <= upper:
            return StrategySignal(
                strategy_name='Donchian_Breakout_Up',
                action='buy',
                confidence=85,
                strength=(current - upper) / upper * 100,
                metadata={
                    'upper': upper,
                    'middle': middle,
                    'lower': lower,
                    'width_percent': (upper - lower) / middle * 100
                },
                price_target=upper * 1.05,
                stop_loss=lower
            )

        # Breakout below channel
        if current < lower * 0.99 and prices[-2] >= lower:
            return StrategySignal(
                strategy_name='Donchian_Breakout_Down',
                action='sell',
                confidence=85,
                strength=(lower - current) / lower * 100,
                metadata={
                    'upper': upper,
                    'lower': lower
                },
                price_target=lower * 0.95,
                stop_loss=upper
            )

        return None

    # Helper methods
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> List[float]:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return []

        deltas = np.diff(prices)
        gains = [max(d, 0) for d in deltas]
        losses = [abs(min(d, 0)) for d in deltas]

        rsi_values = []
        for i in range(period, len(deltas) + 1):
            avg_gain = np.mean(gains[i - period:i])
            avg_loss = np.mean(losses[i - period:i])
            rs = avg_gain / avg_loss if avg_loss > 0 else 0
            rsi = 100 - (100 / (1 + rs))
            rsi_values.append(rsi)

        return rsi_values

    def _calculate_ema(self, data: List[float], period: int) -> List[float]:
        """Calculate EMA"""
        if len(data) < period:
            return []

        multiplier = 2 / (period + 1)
        ema = [np.mean(data[:period])]

        for price in data[period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])

        return ema

    def _calculate_adx(self, highs: List[float], lows: List[float],
                       closes: List[float], period: int = 14) -> Optional[float]:
        """Calculate ADX"""
        if len(highs) < period + 1:
            return None

        tr_list = []
        plus_dm_list = []
        minus_dm_list = []

        for i in range(1, len(highs)):
            tr = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
            tr_list.append(tr)

            plus_dm = highs[i] - highs[i - 1] if highs[i] - highs[i - 1] > lows[i - 1] - lows[i] else 0
            minus_dm = lows[i - 1] - lows[i] if lows[i - 1] - lows[i] > highs[i] - highs[i - 1] else 0

            plus_dm_list.append(max(plus_dm, 0))
            minus_dm_list.append(max(minus_dm, 0))

        if len(tr_list) < period:
            return None

        atr = np.mean(tr_list[-period:])
        plus_di = 100 * np.mean(plus_dm_list[-period:]) / atr if atr > 0 else 0
        minus_di = 100 * np.mean(minus_dm_list[-period:]) / atr if atr > 0 else 0

        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di) if (plus_di + minus_di) > 0 else 0

        return dx


# Pairs Trading Helper
class PairsTradingAnalyzer:
    """Statistical arbitrage between correlated pairs"""

    def __init__(self):
        self.pairs = [
            ('KO', 'PEP'),  # Beverages
            ('JPM', 'BAC'),  # Banks
            ('XOM', 'CVX'),  # Energy
            ('AMD', 'INTC'),  # Semiconductors
            ('V', 'MA'),  # Payment
            ('TSLA', 'RIVN'),  # EVs (speculative)
            ('SPY', 'QQQ'),  # ETFs
        ]

    def analyze_pair(self, symbol1: str, prices1: List[float],
                     symbol2: str, prices2: List[float]) -> Optional[StrategySignal]:
        """Analyze pair for statistical arbitrage"""
        if len(prices1) != len(prices2) or len(prices1) < 30:
            return None

        # Normalize prices
        ratio = [p1 / p2 for p1, p2 in zip(prices1, prices2)]
        mean_ratio = np.mean(ratio)
        std_ratio = np.std(ratio)

        if std_ratio == 0:
            return None

        current_ratio = ratio[-1]
        z_score = (current_ratio - mean_ratio) / std_ratio

        if abs(z_score) > 2:
            # Mean reversion signal
            action = 'buy' if z_score < -2 else 'sell'
            return StrategySignal(
                strategy_name='Pairs_Trading',
                action=action,
                confidence=min(85, abs(z_score) * 20),
                strength=abs(z_score),
                metadata={
                    'pair': f"{symbol1}/{symbol2}",
                    'z_score': z_score,
                    'current_ratio': current_ratio,
                    'mean_ratio': mean_ratio
                }
            )

        return None
