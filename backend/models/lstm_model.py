import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
import joblib
import os
import logging

logger = logging.getLogger(__name__)


# -----------------------------
# PyTorch LSTM Model
# -----------------------------
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size=50, num_layers=2):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2
        )
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]     # last timestep
        out = self.fc(out)
        return out


# -----------------------------
# Predictor Wrapper
# -----------------------------
class LSTMPredictor:
    """PyTorch-based stock price predictor"""
    
    def __init__(self, lookback=60):
        self.lookback = lookback
        self.model = None
        self.scaler = MinMaxScaler()

        self.feature_names = [
            'Close', 'Volume', 'Rsi', 'Macd', 'Sma_20', 'Sma_50',
            'Bb_high', 'Bb_low', 'Atr', 'Volatility'
        ]

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    # ---------------------------------------------------
    def prepare_data(self, df):
        """Prepare sliding window data"""
        data = df[self.feature_names].values
        scaled = self.scaler.fit_transform(data)

        X, y = [], []
        for i in range(self.lookback, len(scaled)):
            X.append(scaled[i-self.lookback:i])
            y.append(scaled[i, 0])

        return np.array(X), np.array(y)

    # ---------------------------------------------------
    def build_model(self, input_shape):
        """Build PyTorch LSTM"""
        input_size = input_shape[1]
        model = LSTMModel(input_size=input_size)
        return model.to(self.device)

    # ---------------------------------------------------
    def train(self, df, epochs=30, batch_size=32):
        logger.info("Training PyTorch LSTM...")

        X, y = self.prepare_data(df)

        # train-test split
        split = int(0.8 * len(X))
        X_train, X_val = X[:split], X[split:]
        y_train, y_val = y[:split], y[split:]

        X_train = torch.tensor(X_train, dtype=torch.float32).to(self.device)
        y_train = torch.tensor(y_train, dtype=torch.float32).to(self.device)
        X_val = torch.tensor(X_val, dtype=torch.float32).to(self.device)
        y_val = torch.tensor(y_val, dtype=torch.float32).to(self.device)

        self.model = self.build_model((X_train.shape[1], X_train.shape[2]))

        criterion = nn.HuberLoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)

        for epoch in range(epochs):
            self.model.train()
            optimizer.zero_grad()

            outputs = self.model(X_train).squeeze()
            loss = criterion(outputs, y_train)
            loss.backward()
            optimizer.step()

            # validation
            self.model.eval()
            with torch.no_grad():
                val_outputs = self.model(X_val).squeeze()
                val_loss = criterion(val_outputs, y_val)

            if epoch % 5 == 0:
                logger.info(f"Epoch {epoch}/{epochs} - Loss: {loss.item():.6f} - Val Loss: {val_loss.item():.6f}")

        logger.info("Training complete.")
        return True

    # ---------------------------------------------------
    def predict(self, df):
        """Predict next day's close price"""
        recent = df[self.feature_names].tail(self.lookback).values
        scaled = self.scaler.transform(recent)

        X = torch.tensor(scaled, dtype=torch.float32).unsqueeze(0).to(self.device)

        self.model.eval()
        with torch.no_grad():
            pred_scaled = self.model(X).cpu().numpy()[0][0]

        # inverse transform
        dummy = np.zeros((1, len(self.feature_names)))
        dummy[0, 0] = pred_scaled
        pred_price = self.scaler.inverse_transform(dummy)[0, 0]

        return float(pred_price)

    # ---------------------------------------------------
    def predict_confidence(self, df):
        pred_price = self.predict(df)
        current_price = df['Close'].iloc[-1]

        volatility = df['Volatility'].iloc[-1]
        confidence = max(0.5, 1 - (volatility * 10))

        return {
            'predicted_price': pred_price,
            'current_price': current_price,
            'change_percent': ((pred_price - current_price) / current_price) * 100,
            'confidence': confidence,
            'direction': 'UP' if pred_price > current_price else 'DOWN'
        }

        # ---------------------------------------------------
    def save(self, model_dir=None):
        # Always save inside backend/models/saved
        base = os.path.dirname(os.path.abspath(__file__))   # backend/models
        save_dir = os.path.join(base, "saved")              # backend/models/saved

        os.makedirs(save_dir, exist_ok=True)

        torch.save(self.model.state_dict(), os.path.join(save_dir, "lstm_model.pt"))
        joblib.dump(self.scaler, os.path.join(save_dir, "scaler.pkl"))

        logger.info(f"Model saved at: {save_dir}")

    # ---------------------------------------------------
    def load(self, model_dir=None):
        # Load from backend/models/saved
        base = os.path.dirname(os.path.abspath(__file__))   # backend/models
        load_dir = os.path.join(base, "saved")              # backend/models/saved

        input_size = len(self.feature_names)
        self.model = LSTMModel(input_size=input_size).to(self.device)

        self.model.load_state_dict(
            torch.load(os.path.join(load_dir, "lstm_model.pt"), map_location=self.device)
        )
        self.scaler = joblib.load(os.path.join(load_dir, "scaler.pkl"))

        logger.info(f"Model loaded from: {load_dir}")


# ---------------------------------------------------
# TRAINING ENTRYPOINT (runs only when executed directly)
# ---------------------------------------------------
if __name__ == "__main__":
    from backend.data.fetcher import StockDataFetcher
    from backend.data.processor import DataProcessor

    print("\n📈 Training LSTM Model (PyTorch)...")

    fetcher = StockDataFetcher()
    df = fetcher.fetch_historical("RELIANCE.NS", "2y")

    processor = DataProcessor()
    df = processor.add_technical_indicators(df)

    predictor = LSTMPredictor()
    predictor.train(df, epochs=30)
    predictor.save()

    print("\n✅ Training complete!")
    print("Model saved in backend/models/saved/")
