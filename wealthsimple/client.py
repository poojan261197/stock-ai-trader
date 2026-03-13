"""
Wealthsimple Trade API Client
Handles account operations, quotes, and trades
"""
from __future__ import annotations

import time
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

from .auth import WealthsimpleAuth


@dataclass
class Position:
    """Stock position"""
    symbol: str
    quantity: float
    book_value: float
    market_value: float
    average_buy_price: float
    currency: str


@dataclass
class Quote:
    """Stock quote"""
    symbol: str
    bid: float
    ask: float
    last_price: float
    change_percent: float
    volume: int
    currency: str
    timestamp: datetime


@dataclass
class Order:
    """Trade order"""
    id: str
    symbol: str
    side: str  # buy or sell
    quantity: float
    price: float
    status: str  # pending, filled, cancelled
    order_type: str  # market, limit
    created_at: datetime


class WealthsimpleClient:
    """
    Wealthsimple Trade API Client
    Official API documentation: https://developers.wealthsimple.com/
    """

    BASE_URL = "https://trade-api.wealthsimple.com"
    GRAPHQL_URL = "https://trade-api.wealthsimple.com/graphql"

    def __init__(self, auth: WealthsimpleAuth):
        self.auth = auth
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self):
        """Setup requests session with authentication"""
        token = self.auth.get_access_token()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "StockPredictionApp/1.0"
        })

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make authenticated request"""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                # Token expired, refresh and retry
                self.auth.refresh_token()
                self._setup_session()
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            raise

    # ========== Accounts ==========

    def get_accounts(self) -> List[Dict]:
        """Get all connected accounts"""
        response = self._request("GET", "/accounts")
        return response.get("results", [])

    def get_account(self, account_id: str) -> Dict:
        """Get specific account details"""
        return self._request("GET", f"/accounts/{account_id}")

    def get_account_balance(self, account_id: str) -> Dict:
        """Get account balance"""
        return self._request("GET", f"/accounts/{account_id}/balances")

    # ========== Positions ==========

    def get_positions(self, account_id: str) -> List[Position]:
        """Get all positions for an account"""
        response = self._request("GET", f"/accounts/{account_id}/positions")
        positions = []

        for item in response.get("results", []):
            positions.append(Position(
                symbol=item.get("stock", {}).get("symbol", ""),
                quantity=float(item.get("quantity", 0)),
                book_value=float(item.get("book_value", 0)),
                market_value=float(item.get("market_value", 0)),
                average_buy_price=float(item.get("average_purchase_price", 0)),
                currency=item.get("currency", "CAD")
            ))

        return positions

    def get_position(self, account_id: str, symbol: str) -> Optional[Position]:
        """Get position for specific symbol"""
        positions = self.get_positions(account_id)
        for pos in positions:
            if pos.symbol == symbol:
                return pos
        return None

    # ========== Quotes ==========

    def get_quote(self, symbol: str) -> Quote:
        """Get real-time quote for a symbol"""
        response = self._request("GET", f"/quotes/{symbol}")
        data = response.get("quote", {})

        return Quote(
            symbol=symbol,
            bid=float(data.get("bid", 0)),
            ask=float(data.get("ask", 0)),
            last_price=float(data.get("amount", 0)),
            change_percent=float(data.get("delta_percent", 0)),
            volume=int(data.get("volume", 0)),
            currency=data.get("currency", "CAD"),
            timestamp=datetime.now()
        )

    def get_quotes(self, symbols: List[str]) -> List[Quote]:
        """Get quotes for multiple symbols"""
        quotes = []
        for symbol in symbols:
            try:
                quote = self.get_quote(symbol)
                quotes.append(quote)
                time.sleep(0.1)  # Rate limiting
            except Exception as e:
                print(f"Error getting quote for {symbol}: {e}")
        return quotes

    # ========== Orders ==========

    def place_order(self, account_id: str, symbol: str, side: str,
                    quantity: float, order_type: str = "market",
                    limit_price: Optional[float] = None) -> Order:
        """
        Place a trade order

        Args:
            account_id: Wealthsimple account ID
            symbol: Stock symbol
            side: "buy" or "sell"
            quantity: Number of shares
            order_type: "market" or "limit"
            limit_price: Limit price (required for limit orders)
        """
        data = {
            "account_id": account_id,
            "security_id": symbol,  # May need to lookup security_id from symbol
            "side": side,
            "quantity": str(quantity),
            "order_type": order_type,
            "marketValue": {  # Only for buy orders
                "amount": str(quantity * (limit_price or 0)),
                "currency": "CAD"
            } if side == "buy" else None
        }

        if order_type == "limit" and limit_price:
            data["limit_price"] = str(limit_price)

        response = self._request("POST", "/orders", json=data)
        order_data = response.get("results", [{}])[0]

        return Order(
            id=order_data.get("id", ""),
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=float(order_data.get("limit_price", order_data.get("market_value", 0))),
            status=order_data.get("status", "unknown"),
            order_type=order_type,
            created_at=datetime.now()
        )

    def get_orders(self, account_id: str, status: str = None) -> List[Order]:
        """Get orders for an account"""
        params = {}
        if status:
            params["status"] = status

        response = self._request("GET", f"/accounts/{account_id}/orders", params=params)
        orders = []

        for item in response.get("results", []):
            orders.append(Order(
                id=item.get("id", ""),
                symbol=item.get("security", {}).get("symbol", ""),
                side=item.get("side", ""),
                quantity=float(item.get("quantity", 0)),
                price=float(item.get("limit_price", item.get("market_value", 0))),
                status=item.get("status", ""),
                order_type=item.get("order_type", "market"),
                created_at=datetime.fromisoformat(item.get("created_at", "").replace('Z', '+00:00'))
            ))

        return orders

    def cancel_order(self, account_id: str, order_id: str) -> bool:
        """Cancel an open order"""
        try:
            self._request("DELETE", f"/accounts/{account_id}/orders/{order_id}")
            return True
        except Exception as e:
            print(f"Error cancelling order: {e}")
            return False

    # ========== Watchlists ==========

    def get_watchlists(self) -> List[Dict]:
        """Get user's watchlists"""
        return self._request("GET", "/watchlists")

    def add_to_watchlist(self, watchlist_id: str, symbol: str):
        """Add symbol to watchlist"""
        return self._request("POST", f"/watchlists/{watchlist_id}/securities", json={"symbol": symbol})

    # ========== Historical Data ==========

    def get_historical_data(self, symbol: str, period: str = "1y") -> List[Dict]:
        """
        Get historical price data

        Args:
            symbol: Stock symbol
            period: 1d, 1w, 1m, 3m, 1y, 5y, all
        """
        return self._request("GET", f"/securities/{symbol}/historical_quotes", params={"period": period})

    # ========== Auto-Trading Integration ==========

    def execute_recommendation(self, account_id: str, recommendation: Dict) -> Optional[Order]:
        """
        Execute a trading recommendation

        Args:
            account_id: Wealthsimple account
            recommendation: {'symbol': str, 'action': str, 'confidence': float}

        Returns:
            Order if placed, None otherwise
        """
        action = recommendation.get("action", "hold").lower()
        symbol = recommendation["symbol"]

        if action == "buy":
            # Get current price
            quote = self.get_quote(symbol)
            price = quote.ask if quote.ask > 0 else quote.last_price

            # Calculate position size (example: 10% of available cash)
            balance = self.get_account_balance(account_id)
            available = float(balance.get("available", {}).get("amount", 0))

            position_size = available * 0.1 / price  # 10% of cash
            min_notional = 100 if "TO" in symbol else 1  # $100 CAD min for Canadian stocks

            if position_size * price >= min_notional:
                return self.place_order(
                    account_id=account_id,
                    symbol=symbol,
                    side="buy",
                    quantity=round(position_size, 4),
                    order_type="market"
                )

        elif action == "sell":
            # Check if we have position
            position = self.get_position(account_id, symbol)
            if position and position.quantity > 0:
                return self.place_order(
                    account_id=account_id,
                    symbol=symbol,
                    side="sell",
                    quantity=position.quantity,
                    order_type="market"
                )

        return None

    def execute_batch_recommendations(self, account_id: str,
                                       recommendations: List[Dict]) -> List[Order]:
        """Execute multiple recommendations"""
        orders = []
        for rec in recommendations:
            try:
                order = self.execute_recommendation(account_id, rec)
                if order:
                    orders.append(order)
                    print(f"Placed {order.side} order for {order.symbol}")
                time.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"Error executing recommendation for {rec.get('symbol')}: {e}")

        return orders
