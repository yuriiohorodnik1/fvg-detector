"""Orchestrates FVG detection over candle data."""

import logging

import pandas as pd

from .fvg import Candle, FVG, detect_fvg
from .notify import send_telegram

logger = logging.getLogger(__name__)


def _row_to_candle(row: pd.Series) -> Candle:
    """Convert a DataFrame row to a Candle."""
    return Candle(
        time=str(row["time"]),
        open=float(row["open"]),
        high=float(row["high"]),
        low=float(row["low"]),
        close=float(row["close"]),
    )


def _format_ts(ts: str) -> str:
    """Format timestamp for display (e.g. 2026-03-12 03:00)."""
    try:
        dt = pd.to_datetime(ts)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(ts)


def _notify(fvg: FVG, ticker: str = "", pip_value: float = 0.0001) -> None:
    """Send notification for a detected FVG (log + Telegram)."""
    prefix = f"[{ticker}] " if ticker else ""
    fvg_hour = _format_ts(fvg.candle2_time)
    gap_pips = (fvg.top - fvg.bottom) / pip_value if pip_value > 0 else 0

    logger.info(
        "%sFVG %s | FVG hour: %s (impulse candle) | top=%.5f bottom=%.5f | %.1f pips | candles %s → %s",
        prefix,
        fvg.kind,
        fvg_hour,
        fvg.top,
        fvg.bottom,
        gap_pips,
        _format_ts(fvg.candle1_time),
        _format_ts(fvg.candle3_time),
    )

    tg = f"FVG {fvg.kind} | {ticker or '?'} | {fvg_hour} | {gap_pips:.1f} pips"
    send_telegram(tg)


def run_detector(
    df: pd.DataFrame,
    ticker: str = "",
    min_gap_pips: float = 3.0,
    pip_value: float = 0.0001,
) -> None:
    """Run FVG detection over candle data.

    At the beginning of each hour, checks the previous three candles for FVG.

    Args:
        df: DataFrame with columns time, open, high, low, close. Must be sorted by time.
        ticker: Optional ticker label for log output.
        min_gap_pips: Minimum gap size in pips to report (filters noise). 0 = no filter.
        pip_value: Price value of 1 pip (0.0001 for forex, 0.1 for XAU).
    """
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)

    min_gap = min_gap_pips * pip_value

    for i in range(3, len(df)):
        candle1 = _row_to_candle(df.iloc[i - 3])
        candle2 = _row_to_candle(df.iloc[i - 2])
        candle3 = _row_to_candle(df.iloc[i - 1])

        fvgs = detect_fvg(candle1, candle2, candle3)
        for fvg in fvgs:
            gap = fvg.top - fvg.bottom
            if min_gap > 0 and gap < min_gap:
                continue
            _notify(fvg, ticker, pip_value)

