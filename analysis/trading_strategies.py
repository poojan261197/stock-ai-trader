"""
Advanced Trading Strategies Module
Includes pattern detection, risk management, and signal generation
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


class PatternType(Enum):
    """Chart and candlestick pattern types"""
    DOJI = "doji"
    HAMMER = "hammer"
    HANGING_MAN = "hanging_man"
    ENGULFING_BULL = "engulfing_bull"
    ENGULFING_BEAR = "engulfing_bear"
    MORNING_STAR = "morning_star"
    EVENING_STAR = "evening_star"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    TRIANGLE_ASCENDING = "triangle_ascending"
    BREAKOUT_UP = "breakout_up"
    BREAKOUT_DOWN = "breakout_down"


@dataclass
class Signal:
    """Trading signal with metadata"""
    pattern: PatternType
    direction: str  # bullish, bearish, neutral
    confidence: float
    price: float
    metadata: Dict


class TradingStrategies:
    """Advanced trading pattern and signal detection"""

    def __init__(self):
        self.patterns = []

    def detect_doji(self, open_price: float, high: float, low: float, close: float) -> Optional[Signal]:
        """Detect Doji pattern"""
        body = abs(close - open_price)
        total_range = high - low
        if total_range == 0 or body / total_range < 0.1:
            return Signal(PatternType.DOJI, "neutral", 60, close, {"body_size": body})
        return None

    def detect_hammer(self, open_price: float, high: float, low: float, close: float) -> Optional[Signal]:
        """Detect Hammer pattern (bullish reversal)"""
        body = abs(close - open_price)
        lower_shadow = min(open_price, close) - low
        upper_shadow = high - max(open_price, close)

        if body == 0:
            return None

        if lower_shadow > 2 * body and upper_shadow < body * 0.5:
            direction = "bullish" if close > open_price else "bearish"
            return Signal(
                PatternType.HAMMER if direction == "bullish" else PatternType.HANGING_MAN,
                direction,
                75,
                close,
                {"lower_shadow": lower_shadow, "body": body}
            )
        return None

    def detect_engulfing(self, prev_open: float, prev_close: float,
                         curr_open: float, curr_close: float) -> Optional[Signal]:
        """Detect Engulfing patterns"""
        prev_body = prev_close - prev_open
        curr_body = curr_close - curr_open

        # Bullish engulfing
        if curr_body > 0 and prev_body < 0:
            if curr_open < prev_close and curr_close > prev_open:
                return Signal(PatternType.ENGULFING_BULL, "bullish", 80, curr_close,
                          {"strength": abs(curr_body / prev_body) if prev_body != 0 else 0})

        # Bearish engulfing
        if curr_body < 0 and prev_body > 0:
            if curr_open > prev_close and curr_close < prev_open:
                return Signal(PatternType.ENGULFING_BEAR, "bearish", 80, curr_close,
                          {"strength": abs(curr_body / prev_body) if prev_body != 0 else 0})

        return None

    def detect_double_top(self, prices: List[float], highs: List[float]) -> Optional[Signal]:
        """Detect Double Top pattern"""
        if len(highs) < 40:
            return None

        # Find local peaks
        peaks = []
        for i in range(2, len(highs) - 2):
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and \
               highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                peaks.append((i, highs[i]))

        if len(peaks) < 2:
            return None

        # Check for two similar highs
        for i in range(len(peaks) - 1):
            for j in range(i + 1, len(peaks)):
                if abs(peaks[i][1] - peaks[j][1]) / peaks[i][1] < 0.03:
                    return Signal(
                        PatternType.DOUBLE_TOP,
                        "bearish",
                        85,
                        prices[-1],
                        {"top1": peaks[i], "top2": peaks[j]}
                    )

        return None

    def detect_double_bottom(self, prices: List[float], lows: List[float]) -> Optional[Signal]:
        """Detect Double Bottom pattern"""
        if len(lows) < 40:
            return None

        # Find local troughs
        troughs = []
        for i in range(2, len(lows) - 2):
            if lows[i] < lows[i-1] and lows[i] < lows[i-2] and \
               lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                troughs.append((i, lows[i]))

        if len(troughs) < 2:
            return None

        # Check for two similar lows
        for i in range(len(troughs) - 1):
            for j in range(i + 1, len(troughs)):
                if abs(troughs[i][1] - troughs[j][1]) / troughs[i][1] < 0.03:
                    return Signal(
                        PatternType.DOUBLE_BOTTOM,
                        "bullish",
                        85,
                        prices[-1],
                        {"bottom1": troughs[i], "bottom2": troughs[j]}
                    )

        return None

    def analyze_candlestick(self, ohlc: List[List[float]]) -> List[Signal]:
        """Analyze candlestick patterns"""
        signals = []

        if len(ohlc) < 2:
            return signals

        curr = ohlc[-1]
        prev = ohlc[-2] if len(ohlc) > 1 else None

        # Single candle patterns
        doji = self.detect_doji(curr[0], curr[1], curr[2], curr[3])
        if doji:
            signals.append(doji)

        hammer = self.detect_hammer(curr[0], curr[1], curr[2], curr[3])
        if hammer:
            signals.append(hammer)

        # Two candle patterns
        if prev:
            engulfing = self.detect_engulfing(
                prev[0], prev[3], curr[0], curr[3]
            )
            if engulfing:
                signals.append(engulfing)

        return signals

    def calculate_risk_metrics(self, entry: float, stop_loss: float,
                               take_profit: float) -> Dict:
        """Calculate risk-reward ratio and position sizing"""
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)
        risk_reward = reward / risk if risk > 0 else 0

        return {
            "risk": risk,
            "reward": reward,
            "risk_reward_ratio": risk_reward,
            "suggested_position_size": min(100, 1 / risk_reward * 10) if risk_reward > 0 else 5
        }

    def calculate_atr(self, highs: List[float], lows: List[float],
                      closes: List[float], period: int = 14) -> float:
        """Calculate Average True Range for volatility"""
        if len(highs) < period + 1:
            return 0

        tr_values = []
        for i in range(1, len(highs)):
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            tr_values.append(max(tr1, tr2, tr3))

        if len(tr_values) >= period:
            return np.mean(tr_values[-period:])
        return 0

    def detect_breakout(self, prices: List[float], highs: List[float],
                       lows: List[float], volume: List[float],
                       lookback: int = 20) -> Optional[Signal]:
        """Detect price breakouts with volume confirmation"""
        if len(prices) < lookback + 5:
            return None

        # Recent resistance/support
        recent_high = max(highs[-lookback:-5])
        recent_low = min(lows[-lookback:-5])
        current_price = prices[-1]
        current_volume = volume[-1] if volume else 0

        # Volume confirmation
        avg_volume = np.mean(volume[-lookback:]) if len(volume) >= lookback else current_volume
        volume_confirm = current_volume > avg_volume * 1.3 if avg_volume > 0 else False

        # Break resistance
        if current_price > recent_high * 1.02 and volume_confirm:
            return Signal(
                PatternType.BREAKOUT_UP,
                "bullish",
                80,
                current_price,
                {
                    "resistance_broken": recent_high,
                    "volume_ratio": current_volume / avg_volume if avg_volume > 0 else 0
                }
            )

        # Break support
        if current_price < recent_low * 0.98 and volume_confirm:
            return Signal(
                PatternType.BREAKOUT_DOWN,
                "bearish",
                80,
                current_price,
                {
                    "support_broken": recent_low,
                    "volume_ratio": current_volume / avg_volume if avg_volume > 0 else 0
                }
            )

        return None

    def get_signals(self, ohlc: List[List[float]], volumes: List[float] = None) -> List[Signal]:
        """Get all trading signals for a stock"""
        signals = []

        if len(ohlc) < 20:
            return signals

        # Extract price components
        opens = [c[0] for c in ohlc]
        highs = [c[1] for c in ohlc]
        lows = [c[2] for c in ohlc]
        closes = [c[3] for c in ohlc]

        # Candlestick patterns
        candle_signals = self.analyze_candlestick(ohlc)
        signals.extend(candle_signals)

        # Chart patterns
        double_top = self.detect_double_top(closes, highs)
        if double_top:
            signals.append(double_top)

        double_bottom = self.detect_double_bottom(closes, lows)
        if double_bottom:
            signals.append(double_bottom)

        # Breakouts
        if volumes:
            breakout = self.detect_breakout(closes, highs, lows, volumes)
            if breakout:
                signals.append(breakout)

        return signals
