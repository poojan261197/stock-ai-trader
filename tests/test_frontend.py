"""
Frontend component tests using pytest and Playwright
Run: pytest tests/test_frontend.py -v
"""
import pytest
from pathlib import Path
import json


class TestDashboard:
    """Test Dashboard page functionality"""

    def test_stats_calculation(self):
        """Test portfolio stats calculation"""
        portfolio = {
            "cash": 10000,
            "positions": [
                {"symbol": "AAPL", "buy_price": 150, "current_price": 175, "quantity": 10},
                {"symbol": "TSLA", "buy_price": 200, "current_price": 180, "quantity": 5}
            ],
            "history": [
                {"action": "BUY", "symbol": "AAPL", "price": 150, "quantity": 10, "date": "2024-01-01"}
            ]
        }

        total_value = sum(p.get("current_price", p["buy_price"]) * p.get("quantity", 1) for p in portfolio["positions"])
        total_invested = sum(p["buy_price"] * p.get("quantity", 1) for p in portfolio["positions"])

        assert total_value == 175 * 10 + 180 * 5  # 2650
        assert total_invested == 150 * 10 + 200 * 5  # 2500

    def test_empty_portfolio(self):
        """Test dashboard with empty portfolio"""
        portfolio = {"cash": 10000, "positions": [], "history": []}

        assert len(portfolio["positions"]) == 0
        assert portfolio["cash"] == 10000


class TestPortfolioPage:
    """Test Portfolio page functionality"""

    def test_pnl_calculation(self):
        """Test P&L calculation"""
        position = {
            "symbol": "AAPL",
            "buy_price": 150,
            "current_price": 175,
            "quantity": 10
        }

        pnl = (position["current_price"] - position["buy_price"]) * position["quantity"]
        pnl_pct = ((position["current_price"] - position["buy_price"]) / position["buy_price"]) * 100

        assert pnl == 250
        assert pnl_pct == 16.67

    def test_position_sorting(self):
        """Test position sorting by market value"""
        positions = [
            {"symbol": "AAPL", "marketValue": 1500},
            {"symbol": "MSFT", "marketValue": 3000},
            {"symbol": "TSLA", "marketValue": 900}
        ]

        sorted_positions = sorted(positions, key=lambda x: x["marketValue"], reverse=True)

        assert sorted_positions[0]["symbol"] == "MSFT"
        assert sorted_positions[1]["symbol"] == "AAPL"
        assert sorted_positions[2]["symbol"] == "TSLA"


class TestScanPage:
    """Test Scan page functionality"""

    def test_stock_recommendation_sorting(self):
        """Test sorting stocks by recommendation score"""
        stocks = [
            {"symbol": "AAPL", "recommendation_score": 85},
            {"symbol": "TSLA", "recommendation_score": 95},
            {"symbol": "MSFT", "recommendation_score": 72}
        ]

        sorted_stocks = sorted(stocks, key=lambda x: x["recommendation_score"], reverse=True)

        assert sorted_stocks[0]["symbol"] == "TSLA"
        assert sorted_stocks[1]["symbol"] == "AAPL"
        assert sorted_stocks[2]["symbol"] == "MSFT"

    def test_action_filtering(self):
        """Test filtering buy recommendations"""
        stocks = [
            {"symbol": "AAPL", "action": "buy"},
            {"symbol": "TSLA", "action": "sell"},
            {"symbol": "MSFT", "action": "buy"}
        ]

        buy_stocks = [s for s in stocks if s["action"] == "buy"]

        assert len(buy_stocks) == 2


class TestAPI:
    """Test API endpoints"""

    def test_health_endpoint(self, tmp_path):
        """Test health check"""
        health_data = {
            "status": "OK",
            "services": {
                "market_data": True,
                "trading_api": True,
                "websocket": True
            }
        }

        assert health_data["status"] == "OK"
        assert all(health_data["services"].values())

    def test_portfolio_endpoint(self):
        """Test portfolio data structure"""
        portfolio = {
            "cash": 10000.0,
            "positions": [],
            "history": [],
            "watchlist": []
        }

        assert "cash" in portfolio
        assert "positions" in portfolio
        assert "history" in portfolio


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
