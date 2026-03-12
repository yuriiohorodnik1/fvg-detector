# FVG Detector

Detects Fair Value Gaps (FVGs) on hourly and intraday candles, with Telegram notifications.

**Supported instruments:** EURUSD, GBPUSD, XAU (Gold), GER40 (DAX), NAS100 (Nasdaq 100)

## Fair Value Gap

A three-candle pattern:

- **Bullish FVG:** Candle 1 high < Candle 3 low
- **Bearish FVG:** Candle 1 low > Candle 3 high

## Setup

```bash
uv sync
```

Create `.env` in the project root:

```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## Usage

```bash
# Run once (1h candles)
uv run python main.py

# 15-minute candles
uv run python main.py --interval 15m

# Daemon mode (runs at :00:30 every hour)
uv run python main.py --schedule --interval 1h
```

**Intervals:** `1m`, `2m`, `5m`, `15m`, `30m`, `1h`, `90m`

## Cron (Kyiv time)

```cron
TZ=Europe/Kyiv

1 8-23 * * 1-5 cd /path/to/fvg-detector && uv run python main.py
```

Runs at minute 1 of hours 8–23, Monday–Friday.

## GitHub Actions

Runs at minute 1 of each hour during market hours (≈ 8–23 Kyiv, Mon–Fri).

### Setup

1. Push the repo to GitHub.
2. Go to **Settings → Secrets and variables → Actions**.
3. Add repository secrets:
   - `TELEGRAM_BOT_TOKEN` — your bot token
   - `TELEGRAM_CHAT_ID` — your chat ID
4. Workflow runs automatically on schedule. Or trigger manually: **Actions → FVG Detector → Run workflow**.

### Schedule (UTC)

Cron: `1 6-21 * * 1-5` — runs at 6:01, 7:01, …, 21:01 UTC, Monday–Friday (≈ 8:01–23:01 Kyiv).

To change hours, edit `.github/workflows/fvg-detector.yml` and adjust the `cron` line.

## Data source

Uses [yfinance](https://github.com/ranaroussi/yfinance) (Yahoo Finance). Data is in UTC.
