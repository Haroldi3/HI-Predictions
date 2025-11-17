from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yfinance as yf, joblib, os, numpy as np
from utils.indicators import add_indicators
from utils.features import make_feature_row
from utils.news import fetch_headlines, avg_vader_sent
from fastapi import HTTPException

app = FastAPI(title = "Stock Trend API")
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
    )

#Health check endpoint
@app.get("/health")
def health():
    return {"status": "ok"}

MODEL_PATH = "models/trend_model.pkl"
model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

class PredictionResponse(BaseModel):
    ticker: str
    direction: str
    confidence: float
    trend_score: float

# Summary endpoint
@app.get("/api/summary")
def summary(ticker: str = Query("AAPL")):
    df = yf.Ticker(ticker).history(period="6mo")
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail=f"No data for ticker {ticker}")
    
    df = add_indicators(df)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No indicator data for ticker {ticker}")
    
    heads = fetch_headlines(ticker)
    sent = avg_vader_sent(heads)
    row = df.dropna().iloc[-1]

    sma_sig = 1 if row["SMA20"] > row["SMA50"] else 0
    macd_sig = 1 if row["MACD"] > 0 else 0
    rsi =float(row["RSI"])
    rsi_sig = (-1 if rsi > 70 else ( 1 if rsi < 30 else 0))

    trend_score = 0.4 * sma_sig + 0.4 * macd_sig + 0.2 * sent + 0.2 * rsi_sig

    return {
        "ticker": ticker.upper(),
        "lastPrice": float(row["Close"]),
        "indicators": {
            "rsi": rsi,
            "sma_signal": sma_sig,
            "macd_signal": macd_sig,
        },
        "sentiment": {
            "avg": sent,
            "n": len(heads)
        },
        "trend_score": trend_score
    }
# Prediction endpoint
@app.get("/api/predict", response_model=PredictionResponse)
def predict(ticker: str = Query("AAPL")):
    df = yf.Ticker(ticker).history(period="6mo")
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail=f"No data for ticker {ticker}")
    
    df = add_indicators(df)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No indicator data for ticker {ticker}")
    
    sent = avg_vader_sent(fetch_headlines(ticker))
    xrow = make_feature_row(df, sent)

    if model is None:
        r = df.dropna().iloc[-1]
        score = (1 if r["SMA20"] > r["SMA50"] else 0) + (1 if r["MACD"] > 0 else 0)
        score = 0.8 * score / 2 + 0.2 * sent
        return PredictionResponse(
            ticker = ticker.upper(),
            direction = ("UP" if score >= 0.5 else "DOWN"),
            confidence = min(0.9, abs(score - 0.5) + 0.5),
            trend_score = score * 2 - 1
        )
    try:
        proba_up = float(model.predict_proba([xrow])[0][1])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model prediction error: {e}")
    
    return PredictionResponse(
        ticker = ticker.upper(),
        direction = ("UP" if proba_up >= 0.5 else "DOWN"),
        confidence = float(max(proba_up,1 - proba_up)),
        trend_score = float(proba_up * 2 - 1)
    )

#JSON Response Model
@app.get("/api/predict", response_model=PredictionResponse)
def predict(ticker: str = Query("AAPL")):
    df = yf.Ticker(ticker).history(period="6mo")
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail=f"No data for ticker {ticker}")
    
    df = add_indicators(df)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No indicator data for ticker {ticker}")
    
    sent = avg_vader_sent(fetch_headlines(ticker))
    xrow = make_feature_row(df, sent)

    if model is None:
        r = df.dropna().iloc[-1]
        score = (1 if r["SMA20"] > r["SMA50"] else 0) + (1 if r["MACD"] > 0 else 0)
        score = 0.8 * score / 2 + 0.2 * sent
        return PredictionResponse(
            ticker = ticker.upper(),
            direction = ("UP" if score >= 0.5 else "DOWN"),
            confidence = min(0.9, abs(score - 0.5) + 0.5),
            trend_score = score * 2 - 1
        )
    try:
        proba_up = float(model.predict_proba([xrow])[0][1])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model prediction error: {e}")
    
    return PredictionResponse(
        ticker = ticker.upper(),
        direction = ("UP" if proba_up >= 0.5 else "DOWN"),
        confidence = float(max(proba_up,1 - proba_up)),
        trend_score = float(proba_up * 2 - 1)
    )
from typing import List
from pydantic import BaseModel

class BatchPredictionRequest(BaseModel):
    tickers: List[str]

@app.post("/api/predict_batch")
def prdeict_batch(body: BatchPredictionRequest):
    responses = []
    for ticker in body.tickers:
        try:
            resp = predict(ticker)
            responses.append(resp)
        except HTTPException as he:
            responses.append({"ticker": ticker.upper(), "error": he.detail})
    return {"results": responses}