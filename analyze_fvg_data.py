"""Analyze FVG data: show raw OHLC for each detected FVG and gap size in pips."""

import pandas as pd
import yfinance as yf

from src.detector.data import load_from_yfinance
from src.detector.fvg import Candle, detect_fvg
from src.detector.runner import _row_to_candle

SYMBOL = "EURUSD=X"


def main() -> None:
    df = load_from_yfinance("EURUSD", period="1d", interval="1h")
    if df.empty:
        print("No data")
        return

    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)

    print("=" * 80)
    print("EURUSD hourly data (yfinance) - timezone: UTC")
    print("=" * 80)
    print(df[["time", "open", "high", "low", "close"]].to_string(index=False))
    print()

    print("=" * 80)
    print("FVG analysis (gap size in pips, 1 pip = 0.0001 for EURUSD)")
    print("=" * 80)

    for i in range(3, len(df)):
        candle1 = _row_to_candle(df.iloc[i - 3])
        candle2 = _row_to_candle(df.iloc[i - 2])
        candle3 = _row_to_candle(df.iloc[i - 1])

        fvgs = detect_fvg(candle1, candle2, candle3)
        for fvg in fvgs:
            gap_pips = (fvg.top - fvg.bottom) / 0.0001
            print(f"\n{fvg.kind.upper()} FVG @ candle {candle3.time}")
            print(f"  Candle 1 ({candle1.time}): O={candle1.open:.5f} H={candle1.high:.5f} L={candle1.low:.5f} C={candle1.close:.5f}")
            print(f"  Candle 2 ({candle2.time}): O={candle2.open:.5f} H={candle2.high:.5f} L={candle2.low:.5f} C={candle2.close:.5f}")
            print(f"  Candle 3 ({candle3.time}): O={candle3.open:.5f} H={candle3.high:.5f} L={candle3.low:.5f} C={candle3.close:.5f}")
            print(f"  Gap: {fvg.bottom:.5f} - {fvg.top:.5f} = {gap_pips:.1f} pips")


if __name__ == "__main__":
    main()
