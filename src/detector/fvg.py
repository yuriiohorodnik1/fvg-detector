"""FVG detection domain logic.

A Fair Value Gap (FVG) is a three-candle pattern:
- Bullish FVG: Candle 1 high < Candle 3 low (imbalance/gap between them)
- Bearish FVG: Candle 1 low > Candle 3 high (imbalance/gap between them)
"""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Candle:
    """OHLC candle data."""

    time: str
    open: float
    high: float
    low: float
    close: float


@dataclass(frozen=True)
class FVG:
    """Detected Fair Value Gap."""

    kind: Literal["bullish", "bearish"]
    top: float
    bottom: float
    candle1_time: str
    candle2_time: str  # Impulse candle (middle) - often used as FVG hour on charts
    candle3_time: str


def detect_fvg(candle1: Candle, candle2: Candle, candle3: Candle) -> list[FVG]:
    """Check if three consecutive candles form an FVG.

    Args:
        candle1: Oldest candle (first of the three)
        candle2: Middle candle
        candle3: Newest candle (third of the three)

    Returns:
        List of detected FVGs (at most one bullish and/or one bearish).
    """
    result: list[FVG] = []

    # Bullish FVG: candle1 high < candle3 low
    if candle1.high < candle3.low:
        result.append(
            FVG(
                kind="bullish",
                top=candle3.low,
                bottom=candle1.high,
                candle1_time=candle1.time,
                candle2_time=candle2.time,
                candle3_time=candle3.time,
            )
        )

    # Bearish FVG: candle1 low > candle3 high
    if candle1.low > candle3.high:
        result.append(
            FVG(
                kind="bearish",
                top=candle1.low,
                bottom=candle3.high,
                candle1_time=candle1.time,
                candle2_time=candle2.time,
                candle3_time=candle3.time,
            )
        )

    return result
