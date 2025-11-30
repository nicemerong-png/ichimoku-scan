import requests
import json
import pandas as pd

symbols = ["btc", "eth", "sol", "xrp", "ada", "doge"]

scan_results = []

def fetch_weekly_ohlc(symbol):
    url = f"https://charts-prod-us.volume-api.pro/coins/{symbol}/candles?interval=1w"
    r = requests.get(url)
    data = r.json()

    # 데이터 없음 방지
    if "candles" not in data:
        return None

    df = pd.DataFrame(data["candles"])
    df.columns = ["timestamp", "open", "high", "low", "close", "volume"]

    return df

def is_ichimoku_bullish(df):
    if len(df) < 52:
        return False

    # Ichimoku
    df["tenkan"] = (df["high"].rolling(9).max() + df["low"].rolling(9).min()) / 2
    df["kijun"] = (df["high"].rolling(26).max() + df["low"].rolling(26).min()) / 2

    df["senkou1"] = ((df["tenkan"] + df["kijun"]) / 2).shift(26)
    df["senkou2"] = ((df["high"].rolling(52).max() + df["low"].rolling(52).min()) / 2).shift(26)

    last = df.iloc[-1]

    return last["senkou1"] > last["senkou2"] and last["close"] > last["senkou1"]

for s in symbols:
    df = fetch_weekly_ohlc(s)
    if df is not None and is_ichimoku_bullish(df):
        scan_results.append(s.upper())

with open("scan_results.json", "w") as f:
    json.dump(scan_results, f, indent=4)

print("Scan complete:", scan_results)
