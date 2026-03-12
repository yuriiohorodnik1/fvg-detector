"""FVG detector entry point."""

import argparse
import logging
import time
from datetime import datetime, timedelta

from src.detector.data import PIP_VALUES, YF_SYMBOLS, load_from_yfinance
from src.detector.runner import run_detector


def main(interval: str = "1h") -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    # Candles to keep: 4 hours of data (enough for 3-candle FVG)
    _mins = {"1m": 1, "2m": 2, "5m": 5, "15m": 15, "30m": 30, "1h": 60, "90m": 90}
    tail_n = max(4, int(4 * 60 / _mins.get(interval, 60)))

    tickers = list(YF_SYMBOLS.keys())

    for ticker in tickers:
        df = load_from_yfinance(ticker, period="1d", interval=interval)
        if df.empty:
            print(f"Skipping {ticker}: no data", flush=True)
            continue

        df = df.sort_values("time").reset_index(drop=True)
        df_tail = df.tail(tail_n)

        if df_tail.empty:
            continue

        last_ts = df_tail["time"].max()
        print(f"\n--- {ticker} ({interval}, {len(df_tail)} candles, up to {last_ts}) ---", flush=True)
        pip_value = PIP_VALUES.get(ticker.upper(), 0.0001)
        run_detector(df_tail, ticker=ticker, min_gap_pips=2.5, pip_value=pip_value)


def _next_run_at_30s() -> datetime:
    """Next :00:30 (30 seconds past the hour)."""
    now = datetime.now()
    next_run = now.replace(minute=0, second=30, microsecond=0)
    if now >= next_run:
        next_run += timedelta(hours=1)
    return next_run


def run_scheduled(interval: str = "1h") -> None:
    """Run detector at 30 seconds past each hour."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    logger = logging.getLogger(__name__)

    while True:
        next_run = _next_run_at_30s()
        wait_sec = (next_run - datetime.now()).total_seconds()
        logger.info("Next run at %s (in %.0fs)", next_run.strftime("%H:%M:%S"), wait_sec)
        time.sleep(wait_sec)
        main(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FVG detector")
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Run at 30 seconds past each hour (daemon mode)",
    )
    parser.add_argument(
        "--interval",
        default="1h",
        choices=["1m", "2m", "5m", "15m", "30m", "1h", "90m"],
        help="Candle interval (default: 1h)",
    )
    args = parser.parse_args()

    if args.schedule:
        run_scheduled(args.interval)
    else:
        main(args.interval)
