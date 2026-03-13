#!/usr/bin/env python3
"""
Daily Stock Market Scanner
Fetches real market data for US + Canada stocks, runs predictions,
and suggests top 5 stocks to trade daily.
"""
from __future__ import annotations

import json
import time
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import yfinance as yf

# Major US + Canada stock symbols (expandable)
DEFAULT_STOCKS = {
    # Dow Jones 30
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "BRK-B", "UNH", "JNJ",
    "JPM", "V", "PG", "MA", "HD", "MRK", "LLY", "PEP", "KO", "AVGO",
    "TMO", "COST", "DIS", "WMT", "ABT", "NKE", "MCD", "ACN", "VZ", "CRM",
    # S&P Tech
    "AMD", "INTC", "CSCO", "ORCL", "IBM", "TXN", "QCOM", "ADBE", "CRM", "INTU",
    "AMAT", "MU", "LRCX", "NOW", "UBER", "SNOW", "PLTR", "ZM", "ROKU", "SQ",
    # Financials
    "BAC", "GS", "MS", "WFC", "C", "AXP", "BLK", "CME", "SPGI", "ICE",
    # Healthcare
    "PFE", "AZN", "BMY", "ABBV", "DHR", "GILD", "GSK", "AMGN", "CVS", "CI",
    # Canada TSX Top
    "SHOP.TO", "TD.TO", "RY.TO", "ENB.TO", "BMO.TO", "BNS.TO", "CNQ.TO",
    "TRP.TO", "SU.TO", "CP.TO", "CNR.TO", "WCN.TO", "CSU.TO", "ATD.TO",
    "BN.TO", "POW.TO", "IFC.TO", "MRU.TO", "DOL.TO", "WN.TO",
}

API_BASE = "http://127.0.0.1:8005"


@dataclass
class StockPrediction:
    symbol: str
    name: str
    price: float
    volume: int
    action: str
    confidence: float
    prob_buy: float
    prob_sell: float
    prob_hold: float
    price_change_24h: float
    price_change_7d: float
    recommendation_score: float
    historical_data: List[Tuple[float, int]]


def api_call(endpoint: str, method: str = "GET", payload: Optional[dict] = None) -> dict:
    """Make API call to the trading agent."""
    url = f"{API_BASE}{endpoint}"
    data = json.dumps(payload).encode() if payload else None
    headers = {"Content-Type": "application/json"} if payload else {}
    req = urllib.request.Request(
        url, data=data, headers=headers, method=method
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def check_api() -> bool:
    """Check if the API is running."""
    try:
        urllib.request.urlopen(f"{API_BASE}/health", timeout=5)
        return True
    except Exception:
        return False


def reset_agent(money: float = 10000) -> None:
    """Reset the agent with fresh capital."""
    try:
        api_call("/reset", "POST", {"money": money})
    except Exception as e:
        print(f"Warning: Could not reset agent: {e}")


def get_stock_data(symbol: str) -> Optional[Tuple[str, List[Tuple[float, int]]]]:
    """
    Fetch historical price and volume data from Yahoo Finance.
    Returns name and list of (close_price, volume) tuples.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        name = info.get("shortName", info.get("longName", symbol))

        # Get last 25 days of data
        hist = ticker.history(period="30d")

        if len(hist) < 20:
            print(f"  {symbol}: Insufficient data ({len(hist)} days)")
            return None

        data = []
        for _, row in hist.iterrows():
            close = float(row["Close"])
            volume = int(row["Volume"])
            data.append((close, volume))

        return name, data

    except Exception as e:
        print(f"  {symbol}: Error fetching data - {e}")
        return None


def process_stock(
    symbol: str, name: str, data: List[Tuple[float, int]]
) -> Optional[StockPrediction]:
    """
    Process stock through the prediction model.
    Feeds historical data and gets prediction for next action.
    """
    try:
        # Feed historical data (first 20 points to fill window)
        for i in range(min(20, len(data) - 1)):
            close, volume = data[i]
            try:
                api_call("/trade", "POST", {"data": [close, volume]})
            except Exception:
                pass  # Continue if some fail

        # Get prediction for latest data point
        latest_close, latest_volume = data[-1]
        prev_close, _ = data[-2] if len(data) > 1 else data[-1]

        result = api_call("/trade", "POST", {"data": [latest_close, latest_volume]})

        # Calculate price changes
        price_change_24h = (
            ((latest_close - prev_close) / prev_close) * 100
            if prev_close > 0
            else 0
        )

        # 7-day change (if available)
        if len(data) >= 7:
            week_ago_close, _ = data[-8]
            price_change_7d = ((latest_close - week_ago_close) / week_ago_close) * 100
        else:
            price_change_7d = 0

        # Extract probabilities
        prob = result.get("probability", [0.33, 0.33, 0.33])
        prob_hold, prob_buy, prob_sell = prob[0], prob[1], prob[2]

        action = result.get("action", "unknown")

        # Calculate recommendation score (0-100)
        # Higher score = better buy opportunity
        score = 0
        if action == "buy":
            score = 50 + prob_buy * 50  # 50-100 range
            if price_change_24h < 0:  # Buying on dip
                score += 10
            if price_change_7d < -5:  # Strong dip
                score += 15
        elif action == "sell":
            score = prob_sell * 30  # 0-30 range
        else:
            score = prob_hold * 40  # 0-40 range

        return StockPrediction(
            symbol=symbol,
            name=name,
            price=latest_close,
            volume=latest_volume,
            action=action,
            confidence=max(prob) * 100,
            prob_buy=prob_buy * 100,
            prob_sell=prob_sell * 100,
            prob_hold=prob_hold * 100,
            price_change_24h=price_change_24h,
            price_change_7d=price_change_7d,
            recommendation_score=score,
            historical_data=data[-30:],
        )

    except Exception as e:
        print(f"  Error processing {symbol}: {e}")
        return None


def scan_market(
    symbols: Optional[set] = None, max_stocks: Optional[int] = None
) -> List[StockPrediction]:
    """
    Scan all stocks and return predictions for each.
    """
    if not check_api():
        print("Error: API not running. Start the server with: python app.py")
        return []

    symbols = symbols or DEFAULT_STOCKS
    results = []

    print(f"\n>> Scanning {len(symbols)} stocks from US + Canada markets...\n")
    print("=" * 70)

    symbol_list = list(symbols)[:max_stocks] if max_stocks else list(symbols)

    for i, symbol in enumerate(symbol_list, 1):
        print(f"[{i:>3}/{len(symbol_list)}] Processing {symbol:>10}...", end=" ")

        # Fetch market data
        data_result = get_stock_data(symbol)
        if not data_result:
            continue

        name, data = data_result

        # Reset agent for each stock (clean slate)
        reset_agent(10000)
        time.sleep(0.1)  # Small delay to not overwhelm API

        # Process through prediction model
        prediction = process_stock(symbol, name, data)
        if prediction:
            results.append(prediction)
            status = "[BUY]" if prediction.action == "buy" else "[SELL]" if prediction.action == "sell" else "[HOLD]"
            print(
                f"{status} {prediction.action.upper():>5} "
                f"(score: {prediction.recommendation_score:.1f})"
            )
        else:
            print("[FAIL] Failed")

    print("=" * 70)
    print(f"\n>> Completed: {len(results)} stocks processed successfully\n")

    return results


def generate_report(
    predictions: List[StockPrediction], output_path: Optional[Path] = None
) -> str:
    """
    Generate a formatted report of top 5 stock recommendations.
    """
    if not predictions:
        return "No predictions available."

    report_lines = []
    report_lines.append("\n" + "=" * 70)
    report_lines.append("TOP 5 DAILY STOCK PICKS - {date}".format(date=datetime.now().strftime("%Y-%m-%d")))
    report_lines.append("=" * 70)
    report_lines.append(f"\nTotal scanned: {len(predictions)} stocks")
    report_lines.append(f"Markets: US (NYSE/NASDAQ) + Canada (TSX)")
    report_lines.append(f"Model: Deep Evolution Strategy")
    report_lines.append(f"\n{'Rank':<6} {'Symbol':<10} {'Action':<8} {'Price':>12} {'7d Change':>10} {'Conf':>8} {'Score':>8}")
    report_lines.append("-" * 70)

    # Sort by recommendation score (descending)
    sorted_stocks = sorted(predictions, key=lambda x: x.recommendation_score, reverse=True)

    # Take top 5 with buy signal
    top_buys = [s for s in sorted_stocks if s.action == "buy"][:5]

    # If less than 5 buys, fill with holds/sells
    if len(top_buys) < 5:
        top_buys += [s for s in sorted_stocks if s.action != "buy"][:5 - len(top_buys)]

    for i, stock in enumerate(top_buys, 1):
        report_lines.append(
            f"{i:<6} {stock.symbol:<10} {stock.action.upper():<8} "
            f"${stock.price:>10.2f} {stock.price_change_7d:>+9.2f}% "
            f"{stock.confidence:>7.0f}% {stock.recommendation_score:>7.1f}"
        )

    report_lines.append("\n" + "-" * 70)
    report_lines.append("\n--- DETAILED ANALYSIS ---\n")

    for i, stock in enumerate(top_buys, 1):
        report_lines.append(f"\n{i}. {stock.symbol} - {stock.name}")
        report_lines.append(f"   Current Price: ${stock.price:.2f}")
        report_lines.append(f"   Recommendation: {stock.action.upper()}")
        report_lines.append(f"   Confidence: {stock.confidence:.1f}%")
        report_lines.append(f"   Buy Probability: {stock.prob_buy:.0f}%")
        report_lines.append(f"   24h Change: {stock.price_change_24h:+.2f}%")
        report_lines.append(f"   7-day Change: {stock.price_change_7d:+.2f}%")
        report_lines.append(f"   Score: {stock.recommendation_score:.2f}/100")

        # Trading suggestion based on action
        if stock.action == "buy":
            if stock.price_change_7d < -5:
                report_lines.append("   TIP Opportunity: Stock is oversold, potential rebound")
            report_lines.append("   * Action: Consider buying on current momentum")
        elif stock.action == "sell":
            report_lines.append("   * Action: Consider profit taking or waiting for dip")
        else:
            report_lines.append("   * Action: Hold current position, monitor for breakout")

    report_lines.append("\n" + "=" * 70)
    report_lines.append("\n*** DISCLAIMER: This is for educational purposes only.")
    report_lines.append("   Do not use for real trading without proper validation.")
    report_lines.append("=" * 70 + "\n")

    report = "\n".join(report_lines)

    # Save to file if path provided
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f">> Report saved to: {output_path}")

    return report


def run_daily_scan():
    """Main entry point - run the daily market scan."""
    print("\n=== DAILY STOCK MARKET SCANNER ===")
    print("   Markets: US (NYSE/NASDAQ) + Canada (TSX)")
    print("   Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()

    # Check API
    if not check_api():
        print("ERROR: Trading API not running!")
        print("   Start it with: cd realtime-agent && python app.py")
        return

    print("OK - API Connected")

    # Run scan (first scan 50 stocks for demo, expand to full list for production)
    predictions = scan_market(max_stocks=50)

    if not predictions:
        print("X No predictions generated. Check API connection.")
        return

    # Generate report
    output_file = Path("daily_picks.txt")
    report = generate_report(predictions, output_path=output_file)

    # Export to JSON for dashboard
    json_file = Path("scan_results.json")
    export_to_json(predictions, path=json_file)

    # Print report
    print(report)

    print(f"\nTIP Your top 5 picks are ready!")
    print(f"   View detailed report in: {output_file.absolute()}")
    print(f"   Dashboard data: {json_file.absolute()}\n")


def export_to_json(predictions: List[StockPrediction], path: Path) -> None:
    """Export predictions to JSON for the dashboard."""
    data = []
    for p in sorted(predictions, key=lambda x: x.recommendation_score, reverse=True)[:5]:
        data.append({
            "symbol": p.symbol,
            "name": p.name,
            "price": round(p.price, 2),
            "action": p.action,
            "confidence": round(p.confidence, 1),
            "score": round(p.recommendation_score, 1),
            "change_24h": round(p.price_change_24h, 2),
            "change_7d": round(p.price_change_7d, 2),
            "probabilities": {
                "buy": round(p.prob_buy, 1),
                "sell": round(p.prob_sell, 1),
                "hold": round(p.prob_hold, 1),
            },
        })

    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().isoformat(),
            "total_scanned": len(predictions),
            "top_picks": data,
        }, f, indent=2)
    print(f"   JSON export: {path}")


if __name__ == "__main__":
    run_daily_scan()
