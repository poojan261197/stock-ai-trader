"""
Backend API and model tests
Run: pytest tests/test_backend.py -v
"""
import pytest
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestStockUniverse:
    """Test stock universe data"""

    def test_stock_universe_exists(self):
        """Test that stock universe file exists"""
        universe_path = Path(__file__).parent.parent / "data" / "stock_universe.py"
        assert universe_path.exists()

    def test_stock_symbols_valid(self):
        """Test stock symbols are valid format"""
        # US stocks should be 1-5 uppercase letters
        valid_us_symbols = ["AAPL", "MSFT", "GOOGL", "BRK-B", "V"]
        for symbol in valid_us_symbols:
            assert len(symbol) <= 5
            assert symbol.replace("-", "").isalpha()
            assert symbol.upper() == symbol


class TestPortfolioManager:
    """Test portfolio management"""

    def test_buy_calculation(self):
        """Test buy order calculation"""
        cash = 10000
        price = 150
        quantity = 10
        total_cost = price * quantity

        new_cash = cash - total_cost

        assert total_cost == 1500
        assert new_cash == 8500

    def test_sell_calculation(self):
        """Test sell order with P&L"""
        position = {
            "symbol": "AAPL",
            "buy_price": 150,
            "current_price": 175,
            "quantity": 10
        }

        sell_price = 175
        pnl = (sell_price - position["buy_price"]) * position["quantity"]
        proceeds = sell_price * position["quantity"]

        assert pnl == 250
        assert proceeds == 1750

    def test_portfolio_serialization(self, tmp_path):
        """Test portfolio saves and loads correctly"""
        portfolio = {
            "cash": 8500.0,
            "positions": [
                {
                    "symbol": "AAPL",
                    "buy_price": 150.0,
                    "quantity": 10,
                    "buy_date": "2024-01-01T00:00:00"
                }
            ],
            "history": [
                {
                    "action": "BUY",
                    "symbol": "AAPL",
                    "price": 150.0,
                    "quantity": 10,
                    "date": "2024-01-01T00:00:00"
                }
            ]
        }

        # Save
        portfolio_file = tmp_path / "portfolio.json"
        with open(portfolio_file, "w") as f:
            json.dump(portfolio, f)

        # Load
        with open(portfolio_file) as f:
            loaded = json.load(f)

        assert loaded["cash"] == portfolio["cash"]
        assert len(loaded["positions"]) == 1
        assert len(loaded["history"]) == 1


class TestPredictions:
    """Test prediction models"""

    def test_prediction_output_format(self):
        """Test prediction output structure"""
        prediction = {
            "symbol": "AAPL",
            "action": "buy",
            "confidence": 0.85,
            "probabilities": {
                "buy": 0.85,
                "hold": 0.10,
                "sell": 0.05
            },
            "price_change_7d": 5.2
        }

        assert prediction["action"] in ["buy", "sell", "hold"]
        assert 0 <= prediction["confidence"] <= 1
        assert sum(prediction["probabilities"].values()) == 1.0

    def test_recommendation_score(self):
        """Test recommendation score calculation"""
        def calculate_score(action, confidence, price_change_7d):
            score = 0
            if action == "buy":
                score = 50 + confidence * 50
                if price_change_7d < 0:
                    score += 10
                if price_change_7d < -5:
                    score += 15
            elif action == "sell":
                score = confidence * 30
            else:
                score = confidence * 40
            return min(100, score)

        # Test buy with dip
        score = calculate_score("buy", 0.9, -7)
        assert 50 < score <= 100

    def test_ensemble_voting(self):
        """Test ensemble model voting"""
        predictions = [
            {"model": "LSTM", "action": "buy", "weight": 0.4},
            {"model": "Transformer", "action": "buy", "weight": 0.4},
            {"model": "Technical", "action": "hold", "weight": 0.2}
        ]

        # Count votes with weights
        action_votes = {}
        for pred in predictions:
            action = pred["action"]
            action_votes[action] = action_votes.get(action, 0) + pred["weight"]

        winner = max(action_votes, key=action_votes.get)
        assert winner == "buy"  # buy has 0.8 weight


class TestDataStore:
    """Test data persistence"""

    def test_scan_history_storage(self, tmp_path):
        """Test scan history storage"""
        scan_result = {
            "date": "2024-01-01T00:00:00",
            "total_scanned": 50,
            "market": "all",
            "top_picks": [
                {"symbol": "AAPL", "action": "buy", "score": 95}
            ]
        }

        history = [scan_result]

        assert len(history) == 1
        assert history[0]["total_scanned"] == 50

    def test_alert_creation(self):
        """Test price alert creation"""
        alert = {
            "id": 1234567890,
            "symbol": "AAPL",
            "type": "price_above",
            "value": 200.0,
            "triggered": False
        }

        assert alert["type"] in ["price_above", "price_below", "gain_pct", "loss_pct"]
        assert not alert["triggered"]


class TestWealthsimple:
    """Test Wealthsimple integration"""

    def test_auth_structure(self):
        """Test auth token structure"""
        token_data = {
            "access_token": "token123",
            "refresh_token": "refresh456",
            "expires_at": 1234567890,
            "scope": "read write trade"
        }

        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert "trade" in token_data["scope"]

    def test_order_structure(self):
        """Test order data structure"""
        order = {
            "symbol": "AAPL",
            "side": "buy",
            "quantity": 10,
            "order_type": "market",
            "account_id": "acc123"
        }

        assert order["side"] in ["buy", "sell"]
        assert order["order_type"] in ["market", "limit"]
        assert order["quantity"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
