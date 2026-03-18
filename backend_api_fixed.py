#!/usr/bin/env python3
"""
Backend API for Stock Prediction System
Fixed version with proper imports
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf

# Add paths
sys.path.insert(0, 'realtime-agent')
sys.path.insert(0, '.')

# Import scanners
try:
    from market_scanner import scan_market
    print("Standard scanner loaded")
except ImportError as e:
    print(f"Standard scanner error: {e}")
    scan_market = None

try:
    from market_scanner_enhanced import enhanced_scan_market
    USE_ENHANCED = True
    print("Enhanced scanner loaded")
except ImportError as e:
    print(f"Enhanced scanner error: {e}")
    enhanced_scan_market = None
    USE_ENHANCED = False

app = Flask(__name__)
CORS(app)

# Data persistence
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

PORTFOLIO_FILE = DATA_DIR / "portfolio.json"
SCAN_HISTORY_FILE = DATA_DIR / "scan_history.json"

class DataStore:
    @staticmethod
    def load_portfolio():
        if PORTFOLIO_FILE.exists():
            with open(PORTFOLIO_FILE, 'r') as f:
                return json.load(f)
        return {"cash": 10000, "positions": [], "history": [], "watchlist": []}

    @staticmethod
    def save_portfolio(data):
        with open(PORTFOLIO_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_scan_history():
        if SCAN_HISTORY_FILE.exists():
            with open(SCAN_HISTORY_FILE, 'r') as f:
                return json.load(f)
        return []

    @staticmethod
    def save_scan_history(scans):
        with open(SCAN_HISTORY_FILE, 'w') as f:
            json.dump(scans[-100:], f, indent=2)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "OK",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "market_data": True,
            "trading_api": True,
            "enhanced_scanner": USE_ENHANCED
        }
    })

@app.route('/api/scan', methods=['POST'])
def trigger_scan():
    try:
        data = request.get_json() or {}
        max_stocks = data.get('max_stocks', 50)

        print(f"Running scan on {max_stocks} stocks...")

        # Use enhanced scanner if available
        if USE_ENHANCED and enhanced_scan_market:
            predictions = enhanced_scan_market(max_stocks=max_stocks, use_ml=False)
            # Convert to dict format
            top_picks = []
            for p in sorted(predictions, key=lambda x: x.recommendation_score, reverse=True)[:5]:
                top_picks.append({
                    "symbol": p.symbol,
                    "name": p.name,
                    "price": p.price,
                    "action": p.action,
                    "confidence": p.confidence,
                    "score": p.recommendation_score,
                    "change_24h": p.price_change_24h,
                    "change_7d": p.price_change_7d,
                    "probabilities": {
                        "buy": p.prob_buy,
                        "sell": p.prob_sell,
                        "hold": p.prob_hold
                    }
                })
        elif scan_market:
            predictions = scan_market(max_stocks=max_stocks)
            top_picks = []
            for p in sorted(predictions, key=lambda x: x.recommendation_score, reverse=True)[:5]:
                top_picks.append({
                    "symbol": p.symbol,
                    "name": p.name,
                    "price": p.price,
                    "action": p.action,
                    "confidence": p.confidence,
                    "score": p.recommendation_score,
                    "change_24h": p.price_change_24h,
                    "change_7d": p.price_change_7d,
                    "probabilities": {
                        "buy": p.prob_buy,
                        "sell": p.prob_sell,
                        "hold": p.prob_hold
                    }
                })
        else:
            return jsonify({"error": "No scanner available"}), 500

        result = {
            "date": datetime.now().isoformat(),
            "total_scanned": len(predictions) if not USE_ENHANCED else len(top_picks) * 2,  # Estimate
            "market": "all",
            "top_picks": top_picks
        }

        DataStore.save_scan_history([result] + DataStore.load_scan_history())
        return jsonify(result)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/scan/results', methods=['GET'])
def get_scan_results():
    history = DataStore.load_scan_history()
    if history:
        return jsonify(history[0])
    return jsonify({"date": datetime.now().isoformat(), "top_picks": []})

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    portfolio = DataStore.load_portfolio()
    # Update prices
    for pos in portfolio.get('positions', []):
        try:
            ticker = yf.Ticker(pos['symbol'])
            hist = ticker.history(period="1d")
            if not hist.empty:
                pos['current_price'] = float(hist['Close'].iloc[-1])
                pos['unrealized_pnl'] = (pos['current_price'] - pos['buy_price']) * pos.get('quantity', 1)
                pos['unrealized_pnl_pct'] = (pos['current_price'] - pos['buy_price']) / pos['buy_price'] * 100
        except:
            pass
    return jsonify(portfolio)

@app.route('/api/portfolio/buy', methods=['POST'])
def buy_stock():
    data = request.get_json()
    symbol = data.get('symbol')
    price = data.get('price')
    quantity = data.get('quantity', 1)

    if not symbol or not price:
        return jsonify({"error": "Missing fields"}), 400

    portfolio = DataStore.load_portfolio()
    total_cost = price * quantity

    if portfolio['cash'] < total_cost:
        return jsonify({"error": "Insufficient cash"}), 400

    position = {
        "symbol": symbol,
        "buy_price": price,
        "current_price": price,
        "quantity": quantity,
        "buy_date": datetime.now().isoformat(),
        "unrealized_pnl": 0,
        "unrealized_pnl_pct": 0
    }

    portfolio['positions'].append(position)
    portfolio['cash'] -= total_cost
    portfolio['history'].append({"action": "BUY", "symbol": symbol, "price": price, "timestamp": datetime.now().isoformat()})

    DataStore.save_portfolio(portfolio)
    return jsonify(portfolio)

@app.route('/api/portfolio/sell', methods=['POST'])
def sell_stock():
    data = request.get_json()
    symbol = data.get('symbol')
    sell_price = data.get('price')

    portfolio = DataStore.load_portfolio()
    positions = [p for p in portfolio['positions'] if p['symbol'] == symbol]

    if not positions:
        return jsonify({"error": "No position found"}), 400

    pos = positions[0]
    portfolio['cash'] += sell_price * pos.get('quantity', 1)
    portfolio['positions'] = [p for p in portfolio['positions'] if p['symbol'] != symbol]
    portfolio['history'].append({"action": "SELL", "symbol": symbol, "price": sell_price, "timestamp": datetime.now().isoformat()})

    DataStore.save_portfolio(portfolio)
    return jsonify(portfolio)

if __name__ == '__main__':
    print("="*50)
    print("Stock Prediction API Server")
    print("="*50)
    print(f"Enhanced Scanner: {USE_ENHANCED}")
    print("="*50)
    print("Starting server on http://localhost:8006")
    app.run(host='0.0.0.0', port=8006, debug=True, use_reloader=False)
