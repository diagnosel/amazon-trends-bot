# Amazon Trends Bot

A Telegram bot built with `aiogram` that finds Amazon US product ideas, matches them with Google Trends keywords, and sends a daily top 5 list of SEO opportunities.

## Features

- `/start` — shows a short introduction and available commands
- `/daily` — returns the latest daily report or generates a new one
- `/keyword <term>` — analyzes a keyword and returns up to 3 relevant product ideas
- daily delivery of the top 5 results to one fixed chat or channel

## Stack

- Python 3.12
- `aiogram` for Telegram
- `APScheduler` for the daily job
- `aiosqlite` for cache and latest report storage
- `keepa` as an optional upgrade for Amazon data
- `pytrends` for Google Trends

## Local Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python -m amazon_trends_bot.main
```

The `.env` file is already created in the project root and is loaded automatically.

## Required Environment Variables

- `BOT_TOKEN`
- `DAILY_CHAT_ID`

## Useful Environment Variables

- `PRODUCT_SOURCE=seed`
- `TIMEZONE=Europe/Kiev`
- `DAILY_HOUR=9`
- `DAILY_MINUTE=0`
- `AMAZON_DOMAIN=US`
- `TRENDS_GEO=US`
- `MAX_RESULTS=5`
- `KEYWORD_DIFFICULTY_THRESHOLD=25`
- `BRANDS=...`
- `KEEPA_CATEGORY_TERMS=...`
- `DATA_DIR=data`
- `SQLITE_PATH=data/bot.sqlite3`
- `KEEPA_API_KEY` is only required if you manually switch `PRODUCT_SOURCE=keepa`

## Railway

This project is designed to run as a single worker process with long polling. The repository already includes `railway.toml` with this start command:

```bash
python -m amazon_trends_bot.main
```

Recommended Railway setup:

1. Connect the GitHub repository.
2. Set the environment variables.
3. Use a single service replica.
4. Optionally mount a volume for `data/` so SQLite and the latest report survive restarts.

## Notes

- `pytrends` uses an unofficial Google Trends API and may be unstable.
- `keyword volume` in this bot is a heuristic estimate based on trend score, not an absolute Google search volume value.
- `SEO difficulty` in v1 is calculated by a mock provider.
- In free mode the bot uses `PRODUCT_SOURCE=seed`, which means an internal catalog of product ideas instead of Keepa.
- In free mode the bot returns Amazon search links for product ideas, not exact product detail pages with real ASINs.
