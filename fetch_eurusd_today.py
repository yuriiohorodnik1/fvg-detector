"""Standalone script: fetch hourly EURUSD data for today."""

import pandas as pd
import yfinance as yf

SYMBOL = "EURUSD=X"


def main() -> None:
    data = yf.download(SYMBOL, period="1d", interval="1h", progress=False, auto_adjust=True)

    if data.empty:
        print("No data available")
        return

    data = data.reset_index()
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [c[0].lower() if isinstance(c, tuple) else str(c).lower() for c in data.columns]
    else:
        data.columns = [str(c).lower() for c in data.columns]
    data = data.rename(columns={data.columns[0]: "time"})
    data = data[["time", "open", "high", "low", "close"]].dropna()
    data["time"] = pd.to_datetime(data["time"])

    print(data.to_string(index=False))


if __name__ == "__main__":
    main()
