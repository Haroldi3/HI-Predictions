import numpy as np
import pandas as pd
import joblib
import os, sys, traceback
import yfinance as yf
from utils.indicators import add_indicators
from sklearn.linear_model import LogisticRegression

def dataset(ticker = "AAPL", period = "12mo") :
    df = yf.Ticker(ticker).history(period=period)
    if df is None or df.empty:
        raise ValueError(f"No data returned for {ticker}")

    # Add indicators
    df = add_indicators(df).dropna()
    # Need enough rows for rolling indicators; otherwise skip
    if len(df) < 60:
        raise ValueError(f"Not enough rows for indicators: {ticker} has {len(df)}")

    # Next-day up/down label
    df["label"] = (df["Close"].shift(-1) > df["Close"]).astype(int)

    # Features (sent placeholder = 0.0 for training)
    X = pd.DataFrame({
        "RSI": df["RSI"],
        "MACD": df["MACD"],
        "sma_gap": df["SMA20"] - df["SMA50"],
        "sent": 0.0
    }).iloc[:-1]
    y = df["label"].iloc[:-1]

    if X.empty or y.empty:
        raise ValueError(f"Empty X/y after processing for {ticker}")

    return X.values, y.values

if __name__ == "__main__":
    print("Starting training...", flush=True)

    tickers = ["AAPL", "MSFT", "NVDA", "AMZN"]
    Xs, ys = [], []

    for t in tickers:
        try:
            print(f"Fetching {t}...", flush=True)
            X, y = dataset(t, period="18mo")   # a bit longer for safety
            Xs.append(X); ys.append(y)
            print(f"OK: {t} -> X{X.shape}, y{y.shape}", flush=True)
        except Exception as e:
            print(f"SKIP {t}: {e}", flush=True)
            traceback.print_exc()

    if not Xs:
        print("ERROR: No datasets loaded. Check internet or yfinance.", file=sys.stderr)
        sys.exit(1)

    print("Stacking datasets...", flush=True)
    X = np.vstack(Xs)
    y = np.concatenate(ys)
    print(f"Final shapes -> X{X.shape}, y{y.shape}", flush=True)

    print("Fitting LogisticRegression...", flush=True)
    model = LogisticRegression(max_iter=1000).fit(X, y)

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/trend_model.pkl")
    print("✅ saved models/trend_model.pkl", flush=True)
