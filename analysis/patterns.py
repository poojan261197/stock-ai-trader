"""
Technical Analysis Patterns & Price Action Detection Module
Identifies chart patterns, candlestick patterns, and key price levels
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from enum import Enum
import statistics

class PatternType(Enum):
    # Trend Patterns
    TREND_UP = "uptrend"
    TREND_DOWN = "downtrend"
    TREND_SIDEWAYS = "sideways"

    # Chart Patterns
    HEAD_AND_SHOULDERS = "head_and_shoulders"
    INV_HEAD_AND_SHOULDERS = "inv_head_and_shoulders"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    TRIPLE_TOP = "triple_top"
    TRIPLE_BOTTOM = "triple_bottom"
    CHANNEL_UP = "channel_up"
    CHANNEL_DOWN = "channel_down"
    TRIANGLE_ASCENDING = "triangle_ascending"
    TRIANGLE_DESCENDING = "triangle_descending"
    TRIANGLE_SYMMETRICAL = "triangle_symmetrical"
    WEDGE_UP = "wedge_up"
    WEDGE_DOWN = "wedge_down"
    FLAG_BULL = "flag_bull"
    FLAG_BEAR = "flag_bear"
    PENNANT = "pennant"
    CUP_AND_HANDLE = "cup_and_handle"
    ROUNDING_BOTTOM = "rounding_bottom"
    ROUNDING_TOP = "rounding_top"
    DIAMOND_TOP = "diamond_top"
    DIAMOND_BOTTOM = "diamond_bottom"

    # Candlestick Patterns
    DOJI = "doji"
    HAMMER = "hammer"
    INV_HAMMER = "inv_hammer"
    HANGING_MAN = "hanging_man"
    SHOOTING_STAR = "shooting_star"
    ENGULFING_BULL = "engulfing_bull"
    ENGULFING_BEAR = "engulfing_bear"
    HARAMI = "harami"
    HARAMI_CROSS = "harami_cross"
    PIERCING_LINE = "piercing_line"
    DARK_CLOUD_COVER = "dark_cloud_cover"
    MORNING_STAR = "morning_star"
    EVENING_STAR = "evening_star"
    THREE_WHITE_SOLDIERS = "three_white_soldiers"
    THREE_BLACK_CROWS = "three_black_crows"
    MARUBOZU_BULL = "marubozu_bull"
    MARUBOZU_BEAR = "marubozu_bear"
    SPINNING_TOP = "spinning_top"
    LONG_LEGGED_DOJI = "long_legged_doji"
    GRAVESTONE_DOJI = "gravestone_doji"
    DRAGONFLY_DOJI = "dragonfly_doji"

    # Key Levels
    SUPPORT = "support"
    RESISTANCE = "resistance"
    BREAKOUT_UP = "breakout_up"
    BREAKOUT_DOWN = "breakout_down"
    PRICE_GAP_UP = "price_gap_up"
    PRICE_GAP_DOWN = "price_gap_down"


def identify_candlestick_patterns(data: pd.DataFrame, lookback: int = 5) -> List[Dict]:
    """Identify candlestick patterns in price data."""
    patterns = []

    if len(data) < 3:
        return patterns

    opens = data['Open'].values
    highs = data['High'].values
    lows = data['Low'].values
    closes = data['Close'].values

    for i in range(2, len(data)):
        o, h, l, c = opens[i], highs[i], lows[i], closes[i]
        prev_o, prev_h, prev_l, prev_c = opens[i-1], highs[i-1], lows[i-1], closes[i-1]
        body = abs(c - o)
        upper_shadow = h - max(o, c)
        lower_shadow = min(o, c) - l
        total_range = h - l

        if total_range == 0:
            continue

        pattern = None
        confidence = 0

        # Doji
        if body / total_range < 0.1:
            pattern = PatternType.DOJI
            confidence = 80

        # Hammer
        if body > 0 and lower_shadow > 2 * body and upper_shadow < body:
            if c > o:  # Bullish
                if c < o:  # After downtrend
                    pattern = PatternType.HAMMER
                    confidence = 85
                else:
                    pattern = PatternType.HANGING_MAN
                    confidence = 75

        # Inverted Hammer
        if body > 0 and upper_shadow > 2 * body and lower_shadow < body:
            if c < o:  # Bearish upper
                pattern = PatternType.INV_HAMMER
                confidence = 80
            else:
                pattern = PatternType.SHOOTING_STAR
                confidence = 75

        # Bullish Engulfing
        if prev_c < prev_o and c > o and o < prev_c and c > prev_o:
            pattern = PatternType.ENGULFING_BULL
            confidence = 85

        # Bearish Engulfing
        if prev_c > prev_o and c < o and o > prev_c and c < prev_o:
            pattern = PatternType.ENGULFING_BEAR
            confidence = 85

        # Morning Star
        if i >= 3:
            prev2_o, prev2_c = opens[i-2], closes[i-2]
            if prev2_c < prev2_o and abs(prev_c - prev_o) < abs(prev2_c - prev2_o) * 0.3 and c > o:
                pattern = PatternType.MORNING_STAR
                confidence = 90

        # Evening Star
        if i >= 3:
            prev2_o, prev2_c = opens[i-2], closes[i-2]
            if prev2_c > prev2_o and abs(prev_c - prev_o) < abs(prev2_c - prev2_o) * 0.3 and c < o:
                pattern = PatternType.EVENING_STAR
                confidence = 90

        # Three White Soldiers
        if i >= 3:
            prev2_o, prev2_c = opens[i-2], closes[i-2]
            if (c > o and prev_c > prev_o and prev2_c > prev2_o and
                c > prev_c > prev2_c and o > prev_o > prev2_o):
                pattern = PatternType.THREE_WHITE_SOLDIERS
                confidence = 90

        # Three Black Crows
        if i >= 3:
            prev2_o, prev2_c = opens[i-2], closes[i-2]
            if (c < o and prev_c < prev_o and prev2_c < prev2_o and
                c < prev_c < prev2_c and o < prev_o < prev2_o):
                pattern = PatternType.THREE_BLACK_CROWS
                confidence = 90

        if pattern:
            patterns.append({
                'type': pattern.value,
                'category': 'candlestick',
                'index': i,
                'confidence': confidence,
                'price': c
            })

    return patterns


def identify_chart_patterns(data: pd.DataFrame) -> List[Dict]:
    """Identify chart patterns in price data."""
    patterns = []

    if len(data) < 50:
        return patterns

    highs = data['High'].values
    lows = data['Low'].values
    closes = data['Close'].values

    # Find local peaks and troughs
    peaks = []
    troughs = []

    for i in range(2, len(highs) - 2):
        # Local peak
        if highs[i] > highs[i-1] and highs[i] > highs[i-2] and \
           highs[i] > highs[i+1] and highs[i] > highs[i+2]:
            peaks.append((i, highs[i]))

        # Local trough
        if lows[i] < lows[i-1] and lows[i] < lows[i-2] and \
           lows[i] < lows[i+1] and lows[i] < lows[i+2]:
            troughs.append((i, lows[i]))

    # Double Top
    if len(peaks) >= 2:
        for i in range(len(peaks) - 1):
            for j in range(i + 1, len(peaks)):
                if abs(peaks[i][1] - peaks[j][1]) / peaks[i][1] < 0.02:
                    patterns.append({
                        'type': PatternType.DOUBLE_TOP.value,
                        'category': 'chart',
                        'confidence': 85,
                        'price': peaks[j][1],
                        'description': 'Two similar highs, potential reversal'
                    })
                    break

    # Double Bottom
    if len(troughs) >= 2:
        for i in range(len(troughs) - 1):
            for j in range(i + 1, len(troughs)):
                if abs(troughs[i][1] - troughs[j][1]) / troughs[i][1] < 0.02:
                    patterns.append({
                        'type': PatternType.DOUBLE_BOTTOM.value,
                        'category': 'chart',
                        'confidence': 85,
                        'price': troughs[j][1],
                        'description': 'Two similar lows, potential reversal'
                    })
                    break

    # Ascending Triangle (higher lows, flat resistance)
    if len(troughs) >= 3:
        recent_troughs = troughs[-5:]
        trough_prices = [t[1] for t in recent_troughs]
        if all(trough_prices[i] <= trough_prices[i+1] for i in range(len(trough_prices)-1)):
            # Check for flat resistance
            recent_peaks = peaks[-5:] if len(peaks) >= 5 else peaks
            if len(recent_peaks) >= 2:
                peak_prices = [p[1] for p in recent_peaks]
                if np.std(peak_prices) / np.mean(peak_prices) < 0.03:
                    patterns.append({
                        'type': PatternType.TRIANGLE_ASCENDING.value,
                        'category': 'chart',
                        'confidence': 80,
                        'price': closes[-1],
                        'description': 'Ascending triangle pattern'
                    })

    # Channel detection
    if len(highs) >= 30:
        recent_highs = highs[-30:]
        recent_lows = lows[-30:]

        # Check for channel up (parallel higher highs and higher lows)
        high_slope, high_intercept = np.polyfit(range(len(recent_highs)), recent_highs, 1)
        low_slope, low_intercept = np.polyfit(range(len(recent_lows)), recent_lows, 1)

        if high_slope > 0.001 and low_slope > 0.001 and abs(high_slope - low_slope) / high_slope < 0.5:
            patterns.append({
                'type': PatternType.CHANNEL_UP.value,
                'category': 'chart',
                'confidence': 75,
                'price': closes[-1],
                'description': f'Upward channel (slope: {high_slope:.4f})'
            })
        elif high_slope < -0.001 and low_slope < -0.001:
            patterns.append({
                'type': PatternType.CHANNEL_DOWN.value,
                'category': 'chart',
                'confidence': 75,
                'price': closes[-1],
                'description': f'Downward channel (slope: {high_slope:.4f})'
            })

    return patterns


def find_support_resistance(data: pd.DataFrame, window: int = 20) -> Dict:
    """Find key support and resistance levels."""
    if len(data) < window:
        return {'support': [], 'resistance': []}

    highs = data['High'].values[-window:]
    lows = data['Low'].values[-window:]
    closes = data['Close'].values

    # Find clusters of similar prices (touch points)
    def find_clusters(prices, tolerance=0.02):
        clusters = []
        sorted_prices = sorted(prices)
        current_cluster = [sorted_prices[0]]

        for price in sorted_prices[1:]:
            if abs(price - np.mean(current_cluster)) / np.mean(current_cluster) < tolerance:
                current_cluster.append(price)
            else:
                if len(current_cluster) >= 2:
                    clusters.append(np.mean(current_cluster))
                current_cluster = [price]

        if len(current_cluster) >= 2:
            clusters.append(np.mean(current_cluster))

        return clusters

    resistance_levels = find_clusters(highs)
    support_levels = find_clusters(lows)

    current_price = closes[-1]

    # Determine nearest levels
    nearest_support = max([s for s in support_levels if s < current_price], default=None)
    nearest_resistance = min([r for r in resistance_levels if r > current_price], default=None)

    return {
        'support_levels': support_levels,
        'resistance_levels': resistance_levels,
        'nearest_support': nearest_support,
        'nearest_resistance': nearest_resistance,
        'current_price': current_price
    }


def calculate_trend_strength(prices: np.ndarray, period: int = 20) -> Dict:
    """Calculate trend strength and direction."""
    if len(prices) < period:
        return {'direction': 'unknown', 'strength': 0}

    recent_prices = prices[-period:]

    # Linear regression slope
    x = np.arange(len(recent_prices))
    slope, intercept = np.polyfit(x, recent_prices, 1)

    # R-squared (trend strength)
    y_pred = slope * x + intercept
    ss_res = np.sum((recent_prices - y_pred) ** 2)
    ss_tot = np.sum((recent_prices - np.mean(recent_prices)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    direction = 'uptrend' if slope > 0 else 'downtrend'
    strength = min(100, r_squared * 100)

    return {
        'direction': direction,
        'strength': float(strength),
        'slope': float(slope),
        'r_squared': float(r_squared)
    }


def analyze_patterns(symbol: str, data: pd.DataFrame) -> Dict:
    """Complete pattern analysis for a stock."""
    if len(data) < 20:
        return {'error': 'Insufficient data'}

    candlestick_patterns = identify_candlestick_patterns(data)
    chart_patterns = identify_chart_patterns(data)
    sr_levels = find_support_resistance(data)
    trend = calculate_trend_strength(data['Close'].values)

    # Combine all patterns
    all_patterns = candlestick_patterns + chart_patterns

    # Count by category
    bullish_count = sum(1 for p in all_patterns if p['type'] in [
        'hammer', 'engulfing_bull', 'morning_star', 'three_white_soldiers',
        'double_bottom', 'inv_head_and_shoulders', 'cup_and_handle',
        'breakout_up', 'doji', 'inv_hammer'
    ])

    bearish_count = sum(1 for p in all_patterns if p['type'] in [
        'hanging_man', 'shooting_star', 'engulfing_bear', 'dark_cloud_cover',
        'evening_star', 'three_black_crows', 'double_top', 'head_and_shoulders',
        'breakout_down', 'gravestone_doji'
    ])

    # Pattern score
    if bullish_count > bearish_count and trend['direction'] == 'uptrend':
        pattern_signal = 'strong_buy'
    elif bullish_count > bearish_count:
        pattern_signal = 'buy'
    elif bearish_count > bullish_count and trend['direction'] == 'downtrend':
        pattern_signal = 'strong_sell'
    elif bearish_count > bullish_count:
        pattern_signal = 'sell'
    else:
        pattern_signal = 'neutral'

    return {
        'symbol': symbol,
        'patterns': all_patterns,
        'pattern_signal': pattern_signal,
        'trend': trend,
        'support_resistance': sr_levels,
        'summary': {
            'bullish_patterns': bullish_count,
            'bearish_patterns': bearish_count,
            'total_patterns': len(all_patterns),
            'trend_direction': trend['direction'],
            'trend_strength': trend['strength']
        }
    }


if __name__ == '__main__':
    import yfinance as yf

    # Test
    ticker = yf.Ticker('AAPL')
    data = ticker.history(period='3mo')

    result = analyze_patterns('AAPL', data)
    print(f"\nPattern Analysis for {result['symbol']}")
    print(f"Signal: {result['pattern_signal']}")
    print(f"Trend: {result['trend']['direction']} (strength: {result['trend']['strength']:.1f})")
    print(f"\nPatterns found: {result['summary']['total_patterns']}")
    for p in result['patterns'][:5]:
        print(f"  - {p['type']} ({p['category']}, confidence: {p['confidence']})")
