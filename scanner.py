import ccxt
import pandas as pd
import numpy as np
import json
from datetime import datetime

exchange = ccxt.bybit()

def ichimoku(df):
    high = df['high']
    low = df['low']

    conv = (high.rolling(9).max() + low.rolling(9).min()) / 2
    base = (high.rolling(26).max() + low.rolling(26).min()) / 2
    spanA = (conv + base) / 2
    spanB = (high.rolling(52).max() + low.rolling(52).min()) / 2

    return spanA, spanB

def fetch_symbols():
    markets = exchange.load_markets()
    return [s for s in markets if s.endswith("/USDT")]

def fetch_weekly(symbol):
    data = exchange.fetch_ohlcv(symbol, timeframe="1w", limit=120)
    df = pd.DataFrame(data, columns=['time','open','high','low','close','volume'])
    return df

def passes(df):
    spanA, spanB = ichimoku(df)
    if len(df) < 60:
        return False

    A = spanA.iloc[-1]
    B = spanB.iloc[-1]
    close = df['close'].iloc[-1]
    open_ = df['open'].iloc[-1]

    return (A > B) and (close > A) and (close > open_)

def run():
    symbols = fetch_symbols()
    good = []

    for sym in symbols:
        try:
            df = fetch_weekly(sym)
            if passes(df):
                good.append(sym)
        except:
            continue

    output = {
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(good),
        "symbols": good
    }

    with open("scan_results.json", "w") as f:
        json.dump(output, f, indent=4)

if __name__ == "__main__":
    run()

