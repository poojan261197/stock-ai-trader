#!/usr/bin/env python3
"""
Enhanced Stock Market Scanner with Multi-Model Ensemble
Integrates LSTM, Transformer, Pattern Analysis, and Technical Strategies
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import warnings

import numpy as np
import pandas as pd
import yfinance as yf
import torch

warnings.filterwarnings('ignore')

# Import our analysis modules
from analysis.patterns import analyze_patterns
from analysis.technical_strategies import MultiStrategyAnalyzer
from analysis.trading_strategies import TradingStrategies, PatternType
from analysis.advanced_strategies import AdvancedStrategyAnalyzer, PairsTradingAnalyzer
from prediction_engine.ensemble import EnsemblePredictor

# Extended stock universe with ETFs
DEFAULT_STOCKS = {
    # US Large Cap
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "BRK-B", "UNH", "JNJ",
    "JPM", "V", "PG", "MA", "HD", "MRK", "LLY", "PEP", "KO", "AVGO",
    "TMO", "COST", "DIS", "WMT", "ABT", "NKE", "MCD", "ACN", "VZ", "CRM",
    # Tech Growth
    "AMD", "INTC", "CSCO", "ORCL", "IBM", "TXN", "QCOM", "ADBE", "INTU",
    "AMAT", "MU", "LRCX", "NOW", "UBER", "SNOW", "PLTR", "ZM", "SQ", "NET",
    # Financials
    "BAC", "GS", "MS", "WFC", "C", "AXP", "BLK", "CME", "SPGI", "ICE",
    # Healthcare
    "PFE", "AZN", "BMY", "ABBV", "DHR", "GILD", "GSK", "AMGN", "CVS", "CI",
    # Energy
    "XOM", "CVX", "COP", "EOG", "SLB", "OXY", "MPC", "VLO", "PSX",
    # US ETFs
    "SPY", "QQQ", "IWM", "DIA", "VTI", "VOO", "ARKK", "ARKG", "ARKW",
    "XLF", "XLK", "XLE", "XLI", "XLU", "XLP", "XLB", "XRT", "SMH", "SOXX",
    "IBIT", "BITO", "GLD", "SLV", "USO", "UNG", "TLT", "IEF", "LQD",
    # Canada TSX
    "SHOP.TO", "TD.TO", "RY.TO", "ENB.TO", "BMO.TO", "BNS.TO", "CNQ.TO",
    "TRP.TO", "SU.TO", "CP.TO", "CNR.TO", "WCN.TO", "CSU.TO", "ATD.TO",
    "BN.TO", "POW.TO", "IFC.TO", "MRU.TO", "DOL.TO", "WN.TO",
    # Canadian ETFs
    "XIU.TO", "XIC.TO", "XUU.TO", "XEF.TO", "ZAG.TO", "ZDV.TO", "XEI.TO",
}


@dataclass
class EnhancedStockPrediction:
    """Enhanced prediction with all model signals."""
    symbol: str
    name: str
    price: float
    volume: int
    price_change_24h: float
    price_change_7d: float
    action: str
    confidence: float
    recommendation_score: float
    prob_buy: float
    prob_sell: float
    prob_hold: float
    lstm_signal: Dict
    transformer_signal: Dict
    patterns: List[Dict]
    strategy_signals: Dict
    trading_cues: Dict
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class EnhancedMarketScanner:
    """Multi-model ensemble scanner."""

    def __init__(self, use_ml: bool = False):
        self.ensemble = None
        self.advanced_strategies = AdvancedStrategyAnalyzer()
        self.pairs_analyzer = PairsTradingAnalyzer()
        if use_ml:
            self._load_ml_models()
        self.strategies = TradingStrategies()
        self.multi_strategy = MultiStrategyAnalyzer()

    def _load_ml_models(self):
        """Load trained ML models."""
        print("Loading ML models...")
        try:
            self.ensemble = EnsemblePredictor()
            print("[OK] ML models loaded")
        except Exception as e:
            print(f"[WARN] Could not load ML models: {e}")
            self.ensemble = None

    def analyze_stock(self, symbol: str) -> Optional[EnhancedStockPrediction]:
        """Analyze a single stock with all models."""
        try:
            # Fetch data
            ticker = yf.Ticker(symbol)
            info = ticker.info
            name = info.get("shortName", info.get("longName", symbol))

            hist = ticker.history(period="90d", interval="1d")
            if len(hist) < 30:
                return None

            df = hist.copy()
            df.reset_index(inplace=True)
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

            # Current stats
            current_price = float(df['Close'].iloc[-1])
            prev_price = float(df['Close'].iloc[-2])
            price_7d_ago = float(df['Close'].iloc[-7]) if len(df) >= 7 else current_price

            volume = int(df['Volume'].iloc[-1])
            change_24h = ((current_price - prev_price) / prev_price) * 100
            change_7d = ((current_price - price_7d_ago) / price_7d_ago) * 100

            prices = df['Close'].tolist()
            highs = df['High'].tolist()
            lows = df['Low'].tolist()
            volumes = df.get('Volume', [0]*len(prices)).tolist()

            # 1. Pattern Analysis
            pattern_analysis = analyze_patterns(symbol, df)

            # 2. Technical Strategies
            strategy_result = self.multi_strategy.analyze(
                symbol=symbol,
                current_price=current_price,
                prices=prices,
                highs=highs,
                lows=lows,
                volumes=volumes
            )

            # 3. Advanced Strategies
            advanced_signals = self.advanced_strategies.analyze(
                symbol, prices, highs, lows, volumes
            )

            # 4. ML Models (if available)
            lstm_signal = {"action": "neutral", "confidence": 0}
            transformer_signal = {"action": "neutral", "confidence": 0}

            if self.ensemble:
                try:
                    ml_pred = self.ensemble.predict(prices, volumes)
                    lstm_action = ml_pred.get('action', 'hold')
                    lstm_conf = ml_pred.get('confidence', 0)
                    lstm_signal = {"action": lstm_action, "confidence": lstm_conf * 100}

                    # Get individual predictions for transformer signal
                    indiv_preds = ml_pred.get('individual_predictions', [])
                    for pred in indiv_preds:
                        if pred.get('model') == 'Transformer':
                            transformer_signal = {
                                "action": pred.get('action', 'hold'),
                                "confidence": pred.get('confidence', 0) * 100
                            }
                except Exception as e:
                    pass

            # 4. Trading Cues
            trading_cues = self._calculate_trading_cues(
                symbol, current_price, prices, volumes, pattern_analysis
            )

            # 5. Ensemble Decision
            final_decision = self._ensemble_decision(
                pattern_analysis, strategy_result, lstm_signal,
                transformer_signal, trading_cues, advanced_signals
            )

            # Calculate risk metrics
            atr = self._calculate_atr(highs, lows, prices)
            stop_loss = current_price - 2 * atr if final_decision['action'] == 'buy' else current_price + 2 * atr
            take_profit = current_price + 3 * atr if final_decision['action'] == 'buy' else current_price - 3 * atr
            risk_reward = abs(take_profit - current_price) / abs(current_price - stop_loss) if stop_loss != current_price else 0

            return EnhancedStockPrediction(
                symbol=symbol,
                name=name,
                price=current_price,
                volume=volume,
                price_change_24h=change_24h,
                price_change_7d=change_7d,
                lstm_signal=lstm_signal,
                transformer_signal=transformer_signal,
                patterns=pattern_analysis.get('patterns', []),
                strategy_signals=strategy_result,
                trading_cues=trading_cues,
                action=final_decision['action'],
                confidence=final_decision['confidence'],
                recommendation_score=final_decision['score'],
                prob_buy=final_decision.get('probs', {}).get('buy', 0),
                prob_sell=final_decision.get('probs', {}).get('sell', 0),
                prob_hold=final_decision.get('probs', {}).get('hold', 0),
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_reward_ratio=risk_reward
            )

        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return None

    def _calculate_trading_cues(self, symbol: str, price: float,
                                prices: List[float], volumes: List[float],
                                pattern_analysis: Dict) -> Dict:
        """Calculate trading cues and context."""
        trend = pattern_analysis.get('trend', {})
        sr = pattern_analysis.get('support_resistance', {})

        cues = []
        confidence = 50

        # Trend cue
        if trend.get('direction') == 'uptrend' and trend.get('strength', 0) > 60:
            cues.append("strong_uptrend")
            confidence += 15
        elif trend.get('direction') == 'downtrend':
            cues.append("downtrend_caution")
            confidence -= 10

        # Support/Resistance proximity
        nearest_support = sr.get('nearest_support')
        nearest_resistance = sr.get('nearest_resistance')

        if nearest_support and price < nearest_support * 1.02:
            cues.append("near_support")
            confidence += 10
        if nearest_resistance and price > nearest_resistance * 0.98:
            cues.append("near_resistance")
            confidence -= 5

        # Volume cue
        if len(volumes) >= 10:
            avg_vol = np.mean(volumes[-10:])
            if volumes[-1] > avg_vol * 1.5:
                cues.append("volume_spike")
                confidence += 10

        return {
            "cues": cues,
            "confidence": min(100, max(0, confidence)),
            "trend_direction": trend.get('direction', 'unknown'),
            "trend_strength": trend.get('strength', 0),
            "nearest_support": nearest_support,
            "nearest_resistance": nearest_resistance
        }

    def _ensemble_decision(self, pattern_analysis: Dict, strategy_result: Dict,
                           lstm_signal: Dict, transformer_signal: Dict,
                           trading_cues: Dict, advanced_signals: List = None) -> Dict:
        """Combine all signals into final decision."""
        votes = {'buy': 0, 'sell': 0, 'hold': 0}
        confidences = []
        if advanced_signals is None:
            advanced_signals = []

        # Pattern signal
        pattern_signal = pattern_analysis.get('pattern_signal', 'neutral')
        if pattern_signal in ['strong_buy', 'buy']:
            votes['buy'] += 1
            confidences.append(70 if pattern_signal == 'buy' else 85)
        elif pattern_signal in ['strong_sell', 'sell']:
            votes['sell'] += 1
            confidences.append(70 if pattern_signal == 'sell' else 85)

        # Strategy signal
        strategy_action = strategy_result.action if hasattr(strategy_result, 'action') else strategy_result.get('action', 'hold')
        if strategy_action == 'buy':
            votes['buy'] += 1
            confidences.append(strategy_result.confidence if hasattr(strategy_result, 'confidence') else strategy_result.get('confidence', 50))
        elif strategy_action == 'sell':
            votes['sell'] += 1
            confidences.append(strategy_result.confidence if hasattr(strategy_result, 'confidence') else strategy_result.get('confidence', 50))

        # ML signals
        if lstm_signal['action'] != 'neutral':
            votes[lstm_signal['action']] += 0.5
            confidences.append(lstm_signal['confidence'])

        if transformer_signal['action'] != 'neutral':
            votes[transformer_signal['action']] += 0.5
            confidences.append(transformer_signal['confidence'])

        # Advanced strategy signals
        for sig in advanced_signals:
            if hasattr(sig, 'action') and sig.action in ['buy', 'sell']:
                votes[sig.action] += 0.4
                confidences.append(sig.confidence if hasattr(sig, 'confidence') else 50)

        # Trading cues
        cue_confidence = trading_cues.get('confidence', 50)
        if 'strong_uptrend' in trading_cues.get('cues', []):
            votes['buy'] += 0.5
        if 'near_support' in trading_cues.get('cues', []):
            votes['buy'] += 0.3

        # Determine action
        max_votes = max(votes.values())
        if max_votes == 0:
            action = 'hold'
        else:
            action = max(votes, key=votes.get)

        # Calculate overall confidence
        avg_confidence = np.mean(confidences) if confidences else 50

        # Calculate probabilities
        total_votes = sum(votes.values())
        if total_votes > 0:
            probs = {
                'buy': min(100, votes['buy'] / total_votes * 100),
                'sell': min(100, votes['sell'] / total_votes * 100),
                'hold': min(100, votes['hold'] / total_votes * 100)
            }
        else:
            probs = {'buy': 25, 'sell': 25, 'hold': 50}

        # Calculate score
        score = avg_confidence * (1 + votes[action])
        if action == 'buy':
            score += pattern_analysis.get('summary', {}).get('bullish_patterns', 0) * 5

        return {
            'action': action,
            'confidence': avg_confidence,
            'score': min(100, score),
            'probs': probs,
            'votes': votes
        }

    def _calculate_atr(self, highs: List[float], lows: List[float], closes: List[float]) -> float:
        """Calculate Average True Range."""
        if len(highs) < 15:
            return 0.0

        tr_values = []
        for i in range(1, len(highs)):
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            tr_values.append(max(tr1, tr2, tr3))

        return np.mean(tr_values[-14:]) if tr_values else 0.0


def enhanced_scan_market(max_stocks: int = 100, symbols: Optional[set] = None,
                         use_ml: bool = False) -> List[EnhancedStockPrediction]:
    """Run enhanced market scan."""
    scanner = EnhancedMarketScanner(use_ml=use_ml)
    symbols = symbols or DEFAULT_STOCKS
    symbol_list = list(symbols)[:max_stocks]

    print(f"\n{'='*70}")
    print(f"ENHANCED MARKET SCANNER")
    print(f"Models: Patterns + Technical Strategies + {'ML Ensemble' if use_ml else 'No ML'}")
    print(f"Scanning {len(symbol_list)} stocks...")
    print(f"{'='*70}")

    results = []
    for i, symbol in enumerate(symbol_list, 1):
        print(f"[{i}/{len(symbol_list)}] Analyzing {symbol}...", end=' ')
        prediction = scanner.analyze_stock(symbol)
        if prediction:
            results.append(prediction)
            print(f"{prediction.action.upper()} (score: {prediction.recommendation_score:.1f})")
        else:
            print("SKIPPED")
        time.sleep(0.1)  # Be nice to yfinance

    print(f"\n{'='*70}")
    print(f"SCAN COMPLETE: {len(results)} stocks analyzed")
    print(f"{'='*70}")
    return results


if __name__ == "__main__":
    # Test run
    results = enhanced_scan_market(max_stocks=10, use_ml=False)
    print("\nTop 5 Buy Recommendations:")
    buys = sorted([r for r in results if r.action == 'buy'],
                  key=lambda x: x.recommendation_score, reverse=True)[:5]
    for r in buys:
        print(f"  {r.symbol}: Score {r.recommendation_score:.1f} (Confidence: {r.confidence:.0f}%)")
