"""
Train LSTM and Transformer models on historical stock data
Downloads data, creates labeled dataset, trains and saves models
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import yfinance as yf
from typing import List, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json
import warnings

warnings.filterwarnings('ignore')

from prediction_engine.lstm_model import AttentionLSTM
from prediction_engine.transformer_model import StockTransformer


class StockDataset(Dataset):
    """Dataset for stock price prediction"""

    def __init__(self, sequences: List[np.ndarray], labels: List[int]):
        self.sequences = sequences
        self.labels = labels

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        return torch.FloatTensor(self.sequences[idx]), torch.LongTensor([self.labels[idx]])[0]


def download_stock_data(symbols: List[str], years: int = 5) -> dict:
    """Download historical data for multiple stocks"""
    print(f"Downloading data for {len(symbols)} stocks...")
    data = {}

    end_date = datetime.now()
    start_date = end_date - timedelta(days=years * 365)

    for i, symbol in enumerate(symbols):
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)

            if len(df) > 100:  # Need enough data
                data[symbol] = {
                    'prices': df['Close'].values.tolist(),
                    'volumes': df['Volume'].values.tolist(),
                    'dates': df.index.tolist()
                }
                print(f"  [{i+1}/{len(symbols)}] {symbol}: {len(df)} days")
            else:
                print(f"  [{i+1}/{len(symbols)}] {symbol}: insufficient data")

        except Exception as e:
            print(f"  [{i+1}/{len(symbols)}] {symbol}: error - {e}")

    return data


def create_labels(prices: List[float], look_ahead: int = 5, threshold: float = 0.02) -> List[int]:
    """
    Create labels based on future returns
    label = 0 (hold), 1 (buy), 2 (sell)
    """
    labels = []
    n = len(prices)

    for i in range(n - look_ahead):
        current_price = prices[i]
        future_price = prices[i + look_ahead]

        return_pct = (future_price - current_price) / current_price

        if return_pct > threshold:  # > 2% gain -> buy
            labels.append(1)
        elif return_pct < -threshold:  # > 2% loss -> sell
            labels.append(2)
        else:  # hold
            labels.append(0)

    # Pad remaining
    labels.extend([0] * look_ahead)

    return labels


def prepare_training_data(stock_data: dict, sequence_length: int = 30) -> Tuple[List[np.ndarray], List[int]]:
    """Prepare sequences and labels for training"""
    sequences = []
    labels = []

    for symbol, data in stock_data.items():
        prices = data['prices']
        volumes = data['volumes']

        # Create labels
        stock_labels = create_labels(prices)

        # Calculate features for each time step
        n = len(prices)
        features = np.zeros((n, 6))

        features[:, 0] = prices
        features[:, 1] = np.log1p(volumes)  # log volume

        # Technical indicators
        for i in range(n):
            if i >= 5:
                features[i, 2] = np.mean(prices[i-4:i+1])  # 5-day SMA
            if i >= 20:
                features[i, 3] = np.mean(prices[i-19:i+1])  # 20-day SMA
            if i > 0:
                features[i, 4] = (prices[i] - prices[i-1]) / prices[i-1] * 100
            if i >= 5:
                features[i, 5] = np.std(prices[i-4:i+1])

        # Normalize
        means = np.mean(features, axis=0)
        stds = np.std(features, axis=0)
        stds[stds == 0] = 1
        normalized = (features - means) / stds

        # Create sequences
        for i in range(sequence_length, n):
            seq = normalized[i-sequence_length:i]
            sequences.append(seq)
            labels.append(stock_labels[i])

    return sequences, labels


def train_lstm(sequences: List[np.ndarray], labels: List[int], epochs: int = 30, batch_size: int = 32):
    """Train LSTM model"""
    print("\n" + "=" * 50)
    print("Training LSTM Model")
    print("=" * 50)

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")

    # Create dataset
    dataset = StockDataset(sequences, labels)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Initialize model
    model = AttentionLSTM(input_size=6, hidden_size=128, num_layers=3, dropout=0.2).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)
    criterion = nn.CrossEntropyLoss()

    # Training loop
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        correct = 0
        total = 0

        for batch_seq, batch_labels in dataloader:
            batch_seq = batch_seq.to(device)
            batch_labels = batch_labels.to(device)

            # Forward
            outputs = model(batch_seq)
            loss = criterion(outputs, batch_labels)

            # Backward
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            # Stats
            total_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += batch_labels.size(0)
            correct += (predicted == batch_labels).sum().item()

        acc = 100 * correct / total
        avg_loss = total_loss / len(dataloader)

        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"Epoch [{epoch+1}/{epochs}] Loss: {avg_loss:.4f} Acc: {acc:.2f}%")

    # Save model
    Path('models').mkdir(exist_ok=True)
    torch.save(model.state_dict(), 'models/lstm_trained.pth')
    print(f"[OK] Saved LSTM model to models/lstm_trained.pth")

    return model


def train_transformer(sequences: List[np.ndarray], labels: List[int], epochs: int = 30, batch_size: int = 32):
    """Train Transformer model"""
    print("\n" + "=" * 50)
    print("Training Transformer Model")
    print("=" * 50)

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")

    # Pad sequences to 8 features for transformer
    sequences_padded = [np.pad(seq, ((0, 0), (0, 2)), mode='constant') for seq in sequences]

    dataset = StockDataset(sequences_padded, labels)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Initialize model
    model = StockTransformer(input_size=8, d_model=128, nhead=8, num_layers=4).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.0005, weight_decay=1e-5)
    criterion = nn.CrossEntropyLoss()

    # Training loop
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        correct = 0
        total = 0

        for batch_seq, batch_labels in dataloader:
            batch_seq = batch_seq.to(device)
            batch_labels = batch_labels.to(device)

            outputs = model(batch_seq)
            loss = criterion(outputs, batch_labels)

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            total_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += batch_labels.size(0)
            correct += (predicted == batch_labels).sum().item()

        acc = 100 * correct / total
        avg_loss = total_loss / len(dataloader)

        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"Epoch [{epoch+1}/{epochs}] Loss: {avg_loss:.4f} Acc: {acc:.2f}%")

    # Save model
    torch.save(model.state_dict(), 'models/transformer_trained.pth')
    print(f"[OK] Saved Transformer model to models/transformer_trained.pth")

    return model


def main():
    """Main training pipeline"""
    print("=" * 50)
    print("Stock Prediction Model Training")
    print("=" * 50)

    # Select stocks for training (diverse set)
    training_symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',  # Tech
        'JPM', 'BAC', 'WFC', 'GS',  # Finance
        'JNJ', 'PFE', 'UNH',  # Healthcare
        'XOM', 'CVX',  # Energy
        'WMT', 'KO', 'PG',  # Consumer
        'SPY', 'QQQ', 'IWM',  # ETFs
        'SHOP.TO', 'TD.TO', 'ENB.TO', 'RY.TO', 'CNR.TO'  # Canadian
    ]

    # Download data
    stock_data = download_stock_data(training_symbols, years=3)

    if len(stock_data) < 5:
        print("ERROR: Not enough data downloaded!")
        return

    print(f"\nDownloaded data for {len(stock_data)} stocks")

    # Prepare training data
    print("\nPreparing training sequences...")
    sequences, labels = prepare_training_data(stock_data, sequence_length=30)

    print(f"Total sequences: {len(sequences)}")

    # Count labels
    unique, counts = np.unique(labels, return_counts=True)
    print("Label distribution:")
    for u, c in zip(unique, counts):
        action = ['hold', 'buy', 'sell'][u]
        print(f"  {action}: {c} ({100*c/len(labels):.1f}%)")

    # Train models
    lstm_model = train_lstm(sequences, labels, epochs=30)
    transformer_model = train_transformer(sequences, labels, epochs=30)

    # Save metadata
    metadata = {
        'trained_at': datetime.now().isoformat(),
        'num_stocks': len(stock_data),
        'num_sequences': len(sequences),
        'symbols': list(stock_data.keys()),
        'epochs': 30,
        'sequence_length': 30
    }

    with open('models/training_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)

    print("\n" + "=" * 50)
    print("Training Complete!")
    print("=" * 50)
    print(f"Trained on {len(stock_data)} stocks")
    print(f"Total training samples: {len(sequences)}")
    print("Models saved to models/")


if __name__ == '__main__':
    main()
