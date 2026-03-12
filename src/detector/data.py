"""Data loading for FVG detector."""

from pathlib import Path

import pandas as pd
import yfinance as yf

# Yahoo Finance symbol mapping for supported tickers
YF_SYMBOLS: dict[str, str] = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "XAU": "GC=F",  # Gold futures
    "GER40": "^GDAXI",  # DAX
    "NAS100": "^NDX",  # Nasdaq 100
}

# Pip value per ticker (for min gap filter). 1 pip = smallest price increment.
PIP_VALUES: dict[str, float] = {
    "EURUSD": 0.0001,
    "GBPUSD": 0.0001,
    "XAU": 0.1,
    "GER40": 1.0,
    "NAS100": 1.0,
}


def load_from_yfinance(
    ticker: str,
    period: str = "60d",
    interval: str = "1h",
) -> pd.DataFrame:
    """Load OHLC data from Yahoo Finance via yfinance.

    Args:
        ticker: Ticker key (EURUSD, GBPUSD, XAU, GER40, NAS100) or raw yfinance symbol.
        period: Data period (e.g. '60d', '1mo', '3mo').
        interval: Candle interval ('1h', '1d', etc.).

    Returns:
        DataFrame with columns time, open, high, low, close.
    """
    symbol = YF_SYMBOLS.get(ticker.upper(), ticker)
    data = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)

    if data.empty:
        return pd.DataFrame()

    data = data.reset_index()
    # Flatten MultiIndex columns (e.g. from multi-symbol download)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [c[0].lower() if isinstance(c, tuple) else str(c).lower() for c in data.columns]
    else:
        data.columns = [str(c).lower() for c in data.columns]
    # Normalize date column (yfinance index becomes 'date' or 'index' after reset_index)
    data = data.rename(columns={data.columns[0]: "time"})
    data = data[["time", "open", "high", "low", "close"]].dropna()
    data["time"] = pd.to_datetime(data["time"])
    return data


def load_csv(path: Path) -> pd.DataFrame:
    """Load OHLC data from CSV."""
    return pd.read_csv(path)
