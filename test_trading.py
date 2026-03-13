#!/usr/bin/env python3
"""Test stock prediction trading with the realtime agent."""
import json
import urllib.request
from typing import Dict, Any

def trade(close: float, volume: float) -> Dict[str, Any]:
    data = json.dumps({'data': [close, volume]}).encode()
    req = urllib.request.Request(
        'http://127.0.0.1:8005/trade',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())

def reset(money: float) -> None:
    data = json.dumps({'money': money}).encode()
    req = urllib.request.Request(
        'http://127.0.0.1:8005/reset',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    urllib.request.urlopen(req, timeout=10)

def get_status():
    req = urllib.request.Request('http://127.0.0.1:8005/health')
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())

def main():
    # Reset with $10,000 capital
    reset(10000)
    print("=" * 60)
    print("STOCK PREDICTION TRADING BOT - Realtime Agent")
    print("=" * 60)
    print(f"Initial Balance: $10,000.00")
    print(f"Window Size: 20 (need 20 points before trading)")
    print()

    # TWTR stock data (actual historical data from 2018)
    twtr_data = [
        (33.42, 13407500), (33.52, 14491900), (33.63, 10424400), (34.04, 22086700), (34.36, 14588200),
        (34.70, 14433200), (36.65, 29583100), (37.88, 32632800), (39.80, 66122200), (40.10, 147805700),
        (39.70, 41573400), (41.21, 34538900), (41.42, 24605300), (43.49, 51155000), (44.07, 35169200),
        (46.76, 50949100), (45.80, 51489600), (46.00, 26025600), (44.95, 39252000), (46.13, 31230200),
        (45.24, 32200300), (45.88, 28628900), (44.17, 31379300), (44.84, 20194100), (43.70, 25875500),
        (44.79, 18911200), (43.67, 24392900), (44.98, 16703600), (43.89, 14237500), (45.06, 16172000),
        (46.65, 23740700), (44.14, 107582400), (43.75, 38467400), (43.87, 35100100), (45.26, 27078500),
        (44.49, 16426700), (44.26, 13012800), (44.71, 20122300), (43.34, 26536800), (42.46, 21712600),
        (44.44, 25067400), (45.10, 16566800), (46.85, 34517100), (47.79, 36317800), (46.71, 11063400)
    ]

    trades = []
    print("Feeding stock data...")
    print("-" * 60)
    print(f"{'Step':>5} | {'Action':>10} | {'Price':>10} | {'Balance':>14} | {'Inventory':>9}")
    print("-" * 60)

    for i, (close, vol) in enumerate(twtr_data):
        result = trade(close, vol)
        action = result['action']

        if action in ['buy', 'sell'] or i == 19 or i >= len(twtr_data) - 5:
            status = get_status()
            inv_size = status.get('inventory_size', 0)
            balance = result['balance']

            if action == 'buy':
                symbol = "BUY >>>"
            elif action == 'sell':
                symbol = "<<< SELL"
            else:
                symbol = "HOLD"
            print(f"{i+1:>5} | {symbol:>10} | ${close:>9.2f} | ${balance:>13,.2f} | {inv_size:>8} units")
            trades.append((i+1, action, close, balance))

    print("-" * 60)
    print(f"\nFinal Status: {get_status()}")

if __name__ == "__main__":
    main()
