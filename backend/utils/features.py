from __future__ import annotations
import pandas as pd

def make_feature_row(df: pd.DataFrame, sent_avg: float) -> list[list[float]]:
    d = df.dropna().iloc[-1]
    sma_gap = float(d["SMA20"] - d["SMA50"])
    return [[float(d["RSI"]), float(d["MACD"]), sma_gap, float(sent_avg)]]