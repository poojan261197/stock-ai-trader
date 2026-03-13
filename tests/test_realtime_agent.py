import csv
import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = REPO_ROOT / "realtime-agent" / "app.py"
REALTIME_AGENT_DIR = REPO_ROOT / "realtime-agent"


def load_app_module():
    if str(REALTIME_AGENT_DIR) not in sys.path:
        sys.path.insert(0, str(REALTIME_AGENT_DIR))
    spec = importlib.util.spec_from_file_location("realtime_agent_app", APP_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class RealtimeAgentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        module = load_app_module()
        csv_path = REPO_ROOT / "realtime-agent" / "TWTR.csv"
        model_path = REPO_ROOT / "realtime-agent" / "model.pkl"
        cls.app = module.create_app(csv_path=csv_path, model_path=model_path)
        cls.client = cls.app.test_client()
        with csv_path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            cls.rows = list(reader)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "OK")

    def test_metadata_endpoint(self):
        response = self.client.get("/metadata")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "OK")
        self.assertEqual(payload["window_size"], 20)
        self.assertIn("dataset", payload)
        self.assertIn("log_level", payload)

    def test_trade_requires_two_values(self):
        response = self.client.post("/trade", json={"data": [1.0]})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_unknown_route_returns_json(self):
        response = self.client.get("/missing-route")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"], "route not found")

    def test_trade_flow_accepts_real_market_rows(self):
        for row in self.rows[:20]:
            response = self.client.post(
                "/trade",
                json={"data": [float(row["Close"]), float(row["Volume"])]},
            )
            self.assertEqual(response.status_code, 200)

        payload = response.get_json()
        self.assertIn(payload["action"], {"buy", "sell", "nothing", "fail"})
        self.assertIn("balance", payload)

    def test_reset_endpoint(self):
        response = self.client.post("/reset", json={"money": 1234.5})
        self.assertEqual(response.status_code, 200)
        balance_response = self.client.get("/balance")
        self.assertEqual(balance_response.status_code, 200)
        self.assertAlmostEqual(balance_response.get_json(), 1234.5)


if __name__ == "__main__":
    unittest.main()
