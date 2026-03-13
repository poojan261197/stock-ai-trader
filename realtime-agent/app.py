from __future__ import annotations

import io
import json
import pickle
import time
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from sklearn.preprocessing import MinMaxScaler

from logging_utils import configure_logging
from settings import AppSettings

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SETTINGS = AppSettings.from_env(BASE_DIR)
window_size = 20
skip = 1
layer_size = 500
output_size = 3


def softmax(z: np.ndarray) -> np.ndarray:
    if z.ndim != 2:
        raise ValueError("softmax expects a 2D array")
    shifted = z - np.max(z, axis=1, keepdims=True)
    exp_shifted = np.exp(shifted)
    return exp_shifted / np.sum(exp_shifted, axis=1, keepdims=True)


def get_state(parameters: list[list[float]], t: int, window: int = window_size) -> np.ndarray:
    outside: list[list[float]] = []
    d = t - window + 1
    for parameter in parameters:
        block = parameter[d : t + 1] if d >= 0 else -d * [parameter[0]] + parameter[0 : t + 1]
        res = []
        for i in range(window - 1):
            res.append(block[i + 1] - block[i])
        for i in range(1, window):
            res.append(block[i] - block[0])
        outside.append(res)
    return np.array(outside, dtype=float).reshape((1, -1))


class Deep_Evolution_Strategy:
    inputs = None

    def __init__(self, weights, reward_function, population_size, sigma, learning_rate):
        self.weights = weights
        self.reward_function = reward_function
        self.population_size = population_size
        self.sigma = sigma
        self.learning_rate = learning_rate

    def _get_weight_from_population(self, weights, population):
        weights_population = []
        for index, value in enumerate(population):
            weights_population.append(weights[index] + self.sigma * value)
        return weights_population

    def get_weights(self):
        return self.weights

    def train(self, epoch: int = 100, print_every: int = 1):
        lasttime = time.time()
        for i in range(epoch):
            population = []
            rewards = np.zeros(self.population_size)
            for _ in range(self.population_size):
                candidate = []
                for weight in self.weights:
                    candidate.append(np.random.randn(*weight.shape))
                population.append(candidate)
            for k in range(self.population_size):
                weights_population = self._get_weight_from_population(self.weights, population[k])
                rewards[k] = self.reward_function(weights_population)
            rewards = (rewards - np.mean(rewards)) / (np.std(rewards) + 1e-7)
            for index, weight in enumerate(self.weights):
                stacked_population = np.array([candidate[index] for candidate in population])
                self.weights[index] = (
                    weight
                    + self.learning_rate
                    / (self.population_size * self.sigma)
                    * np.dot(stacked_population.T, rewards).T
                )
            if (i + 1) % print_every == 0:
                print("iter %d. reward: %f" % (i + 1, self.reward_function(self.weights)))
        print("time taken to train:", time.time() - lasttime, "seconds")


class Model:
    def __init__(self, input_size, layer_size, output_size):
        self.weights = [
            np.random.rand(input_size, layer_size) * np.sqrt(1 / (input_size + layer_size)),
            np.random.rand(layer_size, output_size) * np.sqrt(1 / (layer_size + output_size)),
            np.zeros((1, layer_size)),
            np.zeros((1, output_size)),
        ]

    def predict(self, inputs):
        feed = np.dot(inputs, self.weights[0]) + self.weights[-2]
        return np.dot(feed, self.weights[1]) + self.weights[-1]

    def get_weights(self):
        return self.weights

    def set_weights(self, weights):
        self.weights = weights


class Agent:
    POPULATION_SIZE = 15
    SIGMA = 0.1
    LEARNING_RATE = 0.03

    def __init__(self, model, timeseries, skip, initial_money, real_trend, minmax):
        self.model = model
        self.timeseries = timeseries
        self.skip = skip
        self.real_trend = real_trend
        self.initial_money = initial_money
        self.es = Deep_Evolution_Strategy(
            self.model.get_weights(),
            self.get_reward,
            self.POPULATION_SIZE,
            self.SIGMA,
            self.LEARNING_RATE,
        )
        self.minmax = minmax
        self._initiate()

    def _initiate(self):
        self.trend = self.timeseries[0]
        self._mean = float(np.mean(self.trend))
        self._std = float(np.std(self.trend)) or 1.0
        self._inventory = []
        self._capital = self.initial_money
        self._queue = []
        self._scaled_capital = self.minmax.transform([[self._capital, 2]])[0, 0]

    def reset_capital(self, capital):
        self._capital = capital if capital is not None else self.initial_money
        self._scaled_capital = self.minmax.transform([[self._capital, 2]])[0, 0]
        self._queue = []
        self._inventory = []

    def trade(self, data):
        scaled_data = self.minmax.transform([data])[0]
        real_close = data[0]
        close = scaled_data[0]
        if len(self._queue) >= window_size:
            self._queue.pop(0)
        self._queue.append(scaled_data)
        if len(self._queue) < window_size:
            return {
                "status": "data not enough to trade",
                "action": "fail",
                "balance": self._capital,
                "timestamp": str(datetime.now()),
            }

        state = self.get_state(
            window_size - 1,
            self._inventory,
            self._scaled_capital,
            timeseries=np.array(self._queue).T.tolist(),
        )
        action, probability = self.act_softmax(state)
        if action == 1 and self._scaled_capital >= close:
            self._inventory.append(close)
            self._scaled_capital -= close
            self._capital -= real_close
            return {
                "status": "buy 1 unit, cost %f" % real_close,
                "action": "buy",
                "balance": self._capital,
                "probability": probability.tolist(),
                "timestamp": str(datetime.now()),
            }
        if action == 2 and self._inventory:
            bought_price = self._inventory.pop(0)
            self._scaled_capital += close
            self._capital += real_close
            scaled_bought_price = self.minmax.inverse_transform([[bought_price, 2]])[0, 0]
            invest = ((real_close - scaled_bought_price) / scaled_bought_price) * 100 if scaled_bought_price else 0
            return {
                "status": "sell 1 unit, price %f" % real_close,
                "investment": invest,
                "gain": real_close - scaled_bought_price,
                "balance": self._capital,
                "action": "sell",
                "probability": probability.tolist(),
                "timestamp": str(datetime.now()),
            }
        return {
            "status": "do nothing",
            "action": "nothing",
            "balance": self._capital,
            "probability": probability.tolist(),
            "timestamp": str(datetime.now()),
        }

    def change_data(self, timeseries, skip, initial_money, real_trend, minmax):
        self.timeseries = timeseries
        self.skip = skip
        self.initial_money = initial_money
        self.real_trend = real_trend
        self.minmax = minmax
        self._initiate()

    def act(self, sequence):
        decision = self.model.predict(np.array(sequence))
        return int(np.argmax(decision[0]))

    def act_softmax(self, sequence):
        decision = self.model.predict(np.array(sequence))
        return int(np.argmax(decision[0])), softmax(decision)[0]

    def get_state(self, t, inventory, capital, timeseries):
        state = get_state(timeseries, t)
        len_inventory = len(inventory)
        mean_inventory = float(np.mean(inventory)) if len_inventory else 0.0
        z_inventory = (mean_inventory - self._mean) / self._std
        z_capital = (capital - self._mean) / self._std
        return np.concatenate([state, [[len_inventory, z_inventory, z_capital]]], axis=1)

    def get_reward(self, weights):
        initial_money = self._scaled_capital
        starting_money = initial_money
        invests = []
        self.model.weights = weights
        inventory = []
        state = self.get_state(0, inventory, starting_money, self.timeseries)

        for t in range(0, len(self.trend) - 1, self.skip):
            action = self.act(state)
            if action == 1 and starting_money >= self.trend[t]:
                inventory.append(self.trend[t])
                starting_money -= self.trend[t]
            elif action == 2 and inventory:
                bought_price = inventory.pop(0)
                starting_money += self.trend[t]
                invests.append(((self.trend[t] - bought_price) / bought_price) * 100)
            state = self.get_state(t + 1, inventory, starting_money, self.timeseries)

        mean_invest = float(np.mean(invests)) if invests else 0.0
        score = (starting_money - initial_money) / initial_money * 100
        return mean_invest * 0.7 + score * 0.3

    def fit(self, iterations, checkpoint):
        self.es.train(iterations, print_every=checkpoint)

    def buy(self):
        initial_money = self._scaled_capital
        starting_money = initial_money
        real_initial_money = self.initial_money
        real_starting_money = self.initial_money
        inventory = []
        real_inventory = []
        state = self.get_state(0, inventory, starting_money, self.timeseries)
        states_sell = []
        states_buy = []

        for t in range(0, len(self.trend) - 1, self.skip):
            action, _ = self.act_softmax(state)
            if action == 1 and starting_money >= self.trend[t] and t < (len(self.trend) - 1 - window_size):
                inventory.append(self.trend[t])
                real_inventory.append(self.real_trend[t])
                real_starting_money -= self.real_trend[t]
                starting_money -= self.trend[t]
                states_buy.append(t)
            elif action == 2 and inventory:
                inventory.pop(0)
                real_bought_price = real_inventory.pop(0)
                starting_money += self.trend[t]
                real_starting_money += self.real_trend[t]
                states_sell.append(t)
                _ = ((self.real_trend[t] - real_bought_price) / real_bought_price) * 100 if real_bought_price else 0
            state = self.get_state(t + 1, inventory, starting_money, self.timeseries)

        invest = ((real_starting_money - real_initial_money) / real_initial_money) * 100
        total_gains = real_starting_money - real_initial_money
        return states_buy, states_sell, total_gains, invest


class LegacyModelUnpickler(pickle.Unpickler):
    def find_class(self, module: str, name: str):
        if module == "__main__" and name == "Model":
            return Model
        return super().find_class(module, name)


def load_model(model_path: Path) -> Model:
    with model_path.open("rb") as fopen:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=np.exceptions.VisibleDeprecationWarning)
            return LegacyModelUnpickler(io.BytesIO(fopen.read())).load()


def load_market_data(csv_path: Path):
    frame = pd.read_csv(csv_path)
    required_columns = {"Close", "Volume"}
    missing = required_columns.difference(frame.columns)
    if missing:
        raise ValueError(f"{csv_path} is missing required columns: {sorted(missing)}")

    real_trend = frame["Close"].astype(float).tolist()
    parameters = [real_trend, frame["Volume"].astype(float).tolist()]
    minmax = MinMaxScaler(feature_range=(100, 200)).fit(np.array(parameters).T)
    scaled_parameters = minmax.transform(np.array(parameters).T).T.tolist()
    initial_money = max(parameters[0]) * 2
    return scaled_parameters, real_trend, minmax, initial_money


def build_agent(settings: AppSettings) -> Agent:
    if not settings.data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {settings.data_path}")
    if not settings.model_path.exists():
        raise FileNotFoundError(f"Model not found: {settings.model_path}")

    model = load_model(settings.model_path)
    scaled_parameters, real_trend, minmax, initial_money = load_market_data(settings.data_path)
    return Agent(
        model=model,
        timeseries=scaled_parameters,
        skip=skip,
        initial_money=initial_money,
        real_trend=real_trend,
        minmax=minmax,
    )


def parse_trade_data(payload: Any) -> list[float]:
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, list) or len(payload) != 2:
        raise ValueError("trade data must be a JSON array like [close, volume]")
    return [float(payload[0]), float(payload[1])]


def parse_money(payload: Any) -> float | None:
    if payload is None or payload == "":
        return None
    if isinstance(payload, str):
        payload = json.loads(payload)
    return float(payload)


def create_app(settings: AppSettings | None = None, csv_path: Path | None = None, model_path: Path | None = None) -> Flask:
    effective_settings = settings
    if effective_settings is None:
        base_settings = AppSettings.from_env(BASE_DIR)
        effective_settings = AppSettings(
            base_dir=base_settings.base_dir,
            model_path=Path(model_path).resolve() if model_path is not None else base_settings.model_path,
            data_path=Path(csv_path).resolve() if csv_path is not None else base_settings.data_path,
            host=base_settings.host,
            port=base_settings.port,
            debug=base_settings.debug,
            log_level=base_settings.log_level,
        )

    agent = build_agent(settings=effective_settings)
    app = Flask(__name__)
    configure_logging(app, effective_settings.base_dir, effective_settings.log_level)
    app.config["AGENT"] = agent
    app.config["SETTINGS"] = effective_settings
    app.config["CSV_PATH"] = str(effective_settings.data_path)
    app.config["MODEL_PATH"] = str(effective_settings.model_path)

    @app.before_request
    def log_request():
        app.logger.info("%s %s", request.method, request.path)

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "route not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.exception("Unhandled server error: %s", error)
        return jsonify({"error": "internal server error"}), 500

    @app.get("/")
    def hello():
        return jsonify(
            {
                "status": "OK",
                "message": "Realtime trading agent is ready",
                "dataset": app.config["CSV_PATH"],
                "model": app.config["MODEL_PATH"],
            }
        )

    @app.get("/metadata")
    def metadata():
        current_agent = app.config["AGENT"]
        settings_obj = app.config["SETTINGS"]
        return jsonify(
            {
                "status": "OK",
                "dataset": app.config["CSV_PATH"],
                "model": app.config["MODEL_PATH"],
                "host": settings_obj.host,
                "port": settings_obj.port,
                "debug": settings_obj.debug,
                "log_level": settings_obj.log_level,
                "window_size": window_size,
                "skip": skip,
                "inventory_size": len(current_agent._inventory),
                "queue_length": len(current_agent._queue),
            }
        )

    @app.get("/health")
    def health():
        current_agent = app.config["AGENT"]
        return jsonify(
            {
                "status": "OK",
                "window_size": window_size,
                "queue_length": len(current_agent._queue),
                "inventory_size": len(current_agent._inventory),
                "balance": current_agent._capital,
            }
        )

    @app.get("/inventory")
    def inventory():
        return jsonify(app.config["AGENT"]._inventory)

    @app.get("/queue")
    def queue():
        return jsonify(app.config["AGENT"]._queue)

    @app.get("/balance")
    def balance():
        return jsonify(app.config["AGENT"]._capital)

    @app.route("/trade", methods=["GET", "POST"])
    def trade():
        try:
            payload = request.get_json(silent=True)
            data = payload.get("data") if isinstance(payload, dict) else request.args.get("data")
            parsed = parse_trade_data(data)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            app.logger.warning("Rejected trade payload: %s", exc)
            return jsonify({"error": str(exc)}), 400
        result = app.config["AGENT"].trade(parsed)
        app.logger.info("Trade action=%s balance=%.4f", result["action"], float(result["balance"]))
        return jsonify(result)

    @app.route("/reset", methods=["GET", "POST"])
    def reset():
        try:
            payload = request.get_json(silent=True)
            money = payload.get("money") if isinstance(payload, dict) else request.args.get("money")
            app.config["AGENT"].reset_capital(parse_money(money))
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            app.logger.warning("Rejected reset payload: %s", exc)
            return jsonify({"error": str(exc)}), 400
        app.logger.info("Capital reset to %.4f", float(app.config["AGENT"]._capital))
        return jsonify(True)

    return app


app = create_app(settings=DEFAULT_SETTINGS)


def run_server() -> None:
    from waitress import serve

    app.logger.info(
        "Starting waitress server host=%s port=%s threads=%s",
        DEFAULT_SETTINGS.host,
        DEFAULT_SETTINGS.port,
        8,
    )
    serve(app, host=DEFAULT_SETTINGS.host, port=DEFAULT_SETTINGS.port, threads=8)


if __name__ == "__main__":
    run_server()
