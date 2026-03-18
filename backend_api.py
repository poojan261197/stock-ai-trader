"""
Enhanced Backend API for Stock Prediction System
Includes market scanner endpoints, WebSocket support, and database persistence
"""
from __future__ import annotations

import asyncio
import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import yfinance as yf

# Import from existing app
import sys
sys.path.insert(0, 'realtime-agent')
from app import app as trading_app, create_app, AppSettings

# Import enhanced scanner (with fallback)
try:
    from market_scanner_enhanced import enhanced_scan_market
    USE_ENHANCED = True
except ImportError as e:
    print(f"Warning: Could not load enhanced scanner: {e}")
    USE_ENHANCED = False
    enhanced_scan_market = None

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Data persistence
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

PORTFOLIO_FILE = DATA_DIR / "portfolio.json"
SCAN_HISTORY_FILE = DATA_DIR / "scan_history.json"
ALERTS_FILE = DATA_DIR / "alerts.json"

class DataStore:
    """Simple JSON-based data store"""

    @staticmethod
    def load_portfolio() -> Dict:
        if PORTFOLIO_FILE.exists():
            with open(PORTFOLIO_FILE, 'r') as f:
                return json.load(f)
        return {
            "cash": 10000,
            "positions": [],
            "history": [],
            "watchlist": []
        }

    @staticmethod
    def save_portfolio(data: Dict):
        with open(PORTFOLIO_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_scan_history() -> List:
        if SCAN_HISTORY_FILE.exists():
            with open(SCAN_HISTORY_FILE, 'r') as f:
                return json.load(f)
        return []

    @staticmethod
    def save_scan_history(scans: List):
        with open(SCAN_HISTORY_FILE, 'w') as f:
            json.dump(scans[-100:], f, indent=2)  # Keep last 100

    @staticmethod
    def load_alerts() -> List:
        if ALERTS_FILE.exists():
            with open(ALERTS_FILE, 'r') as f:
                return json.load(f)
        return []

    @staticmethod
    def save_alerts(alerts: List):
        with open(ALERTS_FILE, 'w') as f:
            json.dump(alerts, f, indent=2)

# ============== API ROUTES ==============

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "OK",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "trading_api": True,
            "market_data": True,
            "websocket": True
        }
    })

@app.route('/api/scan', methods=['POST'])
def trigger_scan():
    """Trigger a market scan"""
    try:
        data = request.get_json() or {}
        max_stocks = data.get('max_stocks', 50)
        market = data.get('market', 'all')  # us, ca, tech, all

        # Run scan (this is synchronous for now)
        predictions = scan_market(max_stocks=max_stocks)

        # Sort and take top 5
        top_picks = sorted(
            predictions,
            key=lambda x: x.recommendation_score,
            reverse=True
        )[:5]

        scan_result = {
            "date": datetime.now().isoformat(),
            "total_scanned": len(predictions),
            "market": market,
            "top_picks": [
                {
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
                }
                for p in top_picks
            ]
        }

        # Save to history
        history = DataStore.load_scan_history()
        history.append(scan_result)
        DataStore.save_scan_history(history)

        # Emit to connected clients
        socketio.emit('scan_complete', scan_result)

        return jsonify(scan_result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/scan/results', methods=['GET'])
def get_latest_scan():
    """Get the latest scan results"""
    history = DataStore.load_scan_history()
    if history:
        return jsonify(history[-1])
    return jsonify({"error": "No scan results available"}), 404

@app.route('/api/scan/history', methods=['GET'])
def get_scan_history():
    """Get all scan history"""
    return jsonify(DataStore.load_scan_history())

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """Get current portfolio"""
    portfolio = DataStore.load_portfolio()

    # Update current prices
    for position in portfolio.get('positions', []):
        try:
            ticker = yf.Ticker(position['symbol'])
            hist = ticker.history(period="1d")
            if not hist.empty:
                position['current_price'] = float(hist['Close'].iloc[-1])
                position['unrealized_pnl'] = (
                    position['current_price'] - position['buy_price']
                )
                position['unrealized_pnl_pct'] = (
                    position['unrealized_pnl'] / position['buy_price'] * 100
                )
        except:
            pass

    return jsonify(portfolio)

@app.route('/api/portfolio/buy', methods=['POST'])
def buy_stock():
    """Buy a stock"""
    data = request.get_json()
    symbol = data.get('symbol')
    price = data.get('price')
    quantity = data.get('quantity', 1)

    if not symbol or not price:
        return jsonify({"error": "Symbol and price required"}), 400

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

    portfolio['history'].append({
        "action": "BUY",
        "symbol": symbol,
        "price": price,
        "quantity": quantity,
        "date": datetime.now().isoformat()
    })

    DataStore.save_portfolio(portfolio)

    socketio.emit('portfolio_update', portfolio)

    return jsonify({"success": True, "portfolio": portfolio})

@app.route('/api/portfolio/sell', methods=['POST'])
def sell_stock():
    """Sell a stock"""
    data = request.get_json()
    symbol = data.get('symbol')
    price = data.get('price')

    if not symbol or not price:
        return jsonify({"error": "Symbol and price required"}), 400

    portfolio = DataStore.load_portfolio()

    # Find position
    idx = None
    for i, pos in enumerate(portfolio['positions']):
        if pos['symbol'] == symbol:
            idx = i
            break

    if idx is None:
        return jsonify({"error": "Position not found"}), 404

    position = portfolio['positions'][idx]
    pnl = price - position['buy_price']

    portfolio['cash'] += price
    portfolio['positions'].pop(idx)

    portfolio['history'].append({
        "action": "SELL",
        "symbol": symbol,
        "price": price,
        "buy_price": position['buy_price'],
        "pnl": pnl,
        "pnl_pct": (pnl / position['buy_price']) * 100,
        "date": datetime.now().isoformat()
    })

    DataStore.save_portfolio(portfolio)

    socketio.emit('portfolio_update', portfolio)

    return jsonify({"success": True, "portfolio": portfolio})

@app.route('/api/stocks/quote/<symbol>', methods=['GET'])
def get_stock_quote(symbol):
    """Get real-time stock quote"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="5d")

        return jsonify({
            "symbol": symbol,
            "name": info.get('shortName', info.get('longName', symbol)),
            "price": float(hist['Close'].iloc[-1]) if not hist.empty else None,
            "change": float(hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) if len(hist) > 1 else 0,
            "change_pct": float((hist['Close'].iloc[-1] / hist['Close'].iloc[-2] - 1) * 100) if len(hist) > 1 else 0,
            "volume": int(hist['Volume'].iloc[-1]) if not hist.empty else 0,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    """Get watchlist with current prices"""
    portfolio = DataStore.load_portfolio()
    watchlist = portfolio.get('watchlist', [])

    # Update prices
    updated = []
    for symbol in watchlist:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if not hist.empty:
                updated.append({
                    "symbol": symbol,
                    "price": float(hist['Close'].iloc[-1]),
                    "change_pct": float(
                        (hist['Close'].iloc[-1] / hist['Close'].iloc[-2] - 1) * 100
                    ) if len(hist) > 1 else 0
                })
        except:
            pass

    return jsonify(updated)

@app.route('/api/watchlist', methods=['POST'])
def add_to_watchlist():
    """Add symbol to watchlist"""
    data = request.get_json()
    symbol = data.get('symbol')

    portfolio = DataStore.load_portfolio()
    if 'watchlist' not in portfolio:
        portfolio['watchlist'] = []

    if symbol not in portfolio['watchlist']:
        portfolio['watchlist'].append(symbol)
        DataStore.save_portfolio(portfolio)

    return jsonify({"success": True, "watchlist": portfolio['watchlist']})

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get all alerts"""
    return jsonify(DataStore.load_alerts())

@app.route('/api/alerts', methods=['POST'])
def create_alert():
    """Create a price alert"""
    data = request.get_json()
    alert = {
        "id": int(time.time() * 1000),
        "symbol": data.get('symbol'),
        "type": data.get('type'),  # price_above, price_below, gain_pct, loss_pct
        "value": data.get('value'),
        "created": datetime.now().isoformat(),
        "triggered": False
    }

    alerts = DataStore.load_alerts()
    alerts.append(alert)
    DataStore.save_alerts(alerts)

    return jsonify({"success": True, "alert": alert})

# ============== WEBSOCKET EVENTS ==============

@socketio.on('connect')
def handle_connect():
    """Client connected"""
    emit('connected', {'data': 'Connected to Stock Prediction Server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    print('Client disconnected')

# ============== BACKGROUND TASKS ==============

def check_alerts():
    """Background task to check price alerts"""
    while True:
        try:
            alerts = DataStore.load_alerts()
            portfolio = DataStore.load_portfolio()

            for alert in alerts:
                if alert['triggered']:
                    continue

                try:
                    ticker = yf.Ticker(alert['symbol'])
                    hist = ticker.history(period="1d")
                    if hist.empty:
                        continue

                    current_price = float(hist['Close'].iloc[-1])

                    triggered = False
                    if alert['type'] == 'price_above' and current_price > alert['value']:
                        triggered = True
                    elif alert['type'] == 'price_below' and current_price < alert['value']:
                        triggered = True

                    if triggered:
                        alert['triggered'] = True
                        alert['triggered_at'] = datetime.now().isoformat()
                        alert['triggered_price'] = current_price
                        DataStore.save_alerts(alerts)

                        socketio.emit('alert_triggered', alert)

                except Exception as e:
                    print(f"Error checking alert: {e}")

        except Exception as e:
            print(f"Error in alert checker: {e}")

        time.sleep(60)  # Check every minute

# Start background task
alert_thread = threading.Thread(target=check_alerts, daemon=True)
alert_thread.start()

if __name__ == '__main__':
    print("=" * 60)
    print("Stock Prediction API Server")
    print("=" * 60)
    print("Endpoints:")
    print("  POST /api/scan           - Trigger market scan")
    print("  GET  /api/scan/results   - Get latest scan results")
    print("  GET  /api/portfolio      - Get portfolio")
    print("  POST /api/portfolio/buy  - Buy stock")
    print("  GET  /api/stocks/quote   - Get stock quote")
    print("=" * 60)
    socketio.run(app, host='0.0.0.0', port=8006, debug=True)
