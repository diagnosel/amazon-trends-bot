# Amazon Trends Bot

Русскоязычный Telegram-бот на `aiogram`, который ищет трендовые Amazon US товарные идеи, сопоставляет их с трендовыми запросами из Google Trends и ежедневно отправляет `top 5` SEO-возможностей.

## Что умеет

- `/start` — кратко объясняет, что умеет бот
- `/daily` — показывает последний daily-отчёт или собирает новый
- `/keyword <term>` — анализирует конкретный keyword и показывает до 3 релевантных товарных идей
- ежедневная отправка `top 5` в один фиксированный chat/channel

## Стек

- Python 3.12
- `aiogram` для Telegram
- `APScheduler` для daily job
- `aiosqlite` для хранения cache и latest report
- `keepa` как optional upgrade для Amazon данных
- `pytrends` для Google Trends

## Быстрый старт локально

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python -m amazon_trends_bot.main
```

Файл `.env` уже создан в корне проекта и загружается автоматически.

## Обязательные env

- `BOT_TOKEN`
- `DAILY_CHAT_ID`

## Полезные env с дефолтами

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
- `KEEPA_API_KEY` нужен только если вручную переключишь `PRODUCT_SOURCE=keepa`

## Railway

Проект рассчитан на один worker-процесс с long polling. В репозитории уже есть `railway.toml` со start command:

```bash
python -m amazon_trends_bot.main
```

Для Railway стоит:

1. Подключить GitHub-репозиторий.
2. Задать env vars.
3. Использовать одну реплику сервиса.
4. При необходимости примонтировать volume для `data/`, чтобы SQLite и latest report переживали рестарты.

## Важные замечания

- `pytrends` использует неофициальный API Google Trends и может быть нестабилен.
- `keyword volume` в этом боте — эвристическая оценка на основе trend score, а не абсолютный поисковый объём от Google.
- `SEO difficulty` в v1 рассчитывается mock-провайдером.
- В бесплатном режиме бот использует `PRODUCT_SOURCE=seed`, то есть внутренний каталог товарных идей без Keepa.
