# src/alpaca/market_data.py
from datetime import datetime, timedelta
import pandas as pd

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed

from src.utils import config
from src.utils.logger import get_logger

log = get_logger("alpaca.market_data")


def get_data_client() -> StockHistoricalDataClient:
    return StockHistoricalDataClient(
        api_key=config.ALPACA_API_KEY,
        secret_key=config.ALPACA_SECRET_KEY,
    )


def get_bars(symbol: str, days: int = 200) -> pd.DataFrame:
    """Symbol ke liye pichle `days` din ke daily bars laao."""
    client = get_data_client()
    end = datetime.now()
    start = end - timedelta(days=days)

    request = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Day,
        start=start,
        end=end,
        feed=DataFeed.IEX,   # free (paper) plan IEX data use karta hai
    )
    bars = client.get_stock_bars(request)
    df = bars.df

    if df.empty:
        raise RuntimeError(f"{symbol} ke liye koi data nahi mila.")

    # Single symbol par index MultiIndex hota hai (symbol, timestamp) — flatten karo
    if isinstance(df.index, pd.MultiIndex):
        df = df.reset_index(level=0, drop=True)

    log.info("Fetched %d daily bars for %s", len(df), symbol)
    return df


# ---------- Indicators (pure pandas, koi extra library nahi) ----------

def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window).mean()


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    macd_line = ema(series, fast) - ema(series, slow)
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    return tr.rolling(window=period).mean()


def compute_indicators(symbol: str, days: int = 200) -> dict:
    """Bars laao, indicators nikaalo, latest values ka clean summary do."""
    df = get_bars(symbol, days)
    close = df["close"]

    df["sma20"] = sma(close, 20)
    df["sma50"] = sma(close, 50)
    df["rsi"] = rsi(close, 14)
    macd_line, signal_line, _ = macd(close)
    df["macd"] = macd_line
    df["macd_signal"] = signal_line
    df["atr"] = atr(df, 14)

    latest = df.iloc[-1]

    summary = {
        "symbol": symbol,
        "price": round(float(latest["close"]), 2),
        "sma20": round(float(latest["sma20"]), 2),
        "sma50": round(float(latest["sma50"]), 2),
        "rsi": round(float(latest["rsi"]), 2),
        "macd": round(float(latest["macd"]), 3),
        "macd_signal": round(float(latest["macd_signal"]), 3),
        "atr": round(float(latest["atr"]), 2),
        "volume": int(latest["volume"]),
    }
    return summary