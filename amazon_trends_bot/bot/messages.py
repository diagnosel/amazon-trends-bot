from __future__ import annotations

from zoneinfo import ZoneInfo

from amazon_trends_bot.config import Settings
from amazon_trends_bot.domain.models import DailyReport, KeywordCommandResult, ProductKeywordMatch


def compose_start_message(settings: Settings) -> str:
    return (
        "Привет! Я ищу SEO-возможности на стыке Amazon US и Google Trends US.\n\n"
        "Что я умею:\n"
        "/daily — показать последний daily top 5\n"
        "/keyword <term> — проверить отдельный keyword\n\n"
        "По умолчанию я работаю с Amazon US, Google Trends US и исключаю брендовые запросы."
    )


def compose_daily_report(report: DailyReport, settings: Settings) -> str:
    local_dt = report.generated_at.astimezone(ZoneInfo(settings.timezone))
    has_seed_items = any(match.product.asin.startswith("SEED") for match in report.matches)
    header = [
        "Ежедневный top 5 по товарам и SEO-запросам",
        f"Собрано: {local_dt.strftime('%Y-%m-%d %H:%M %Z')}",
    ]
    if has_seed_items:
        header.append("Free mode: links below open Amazon search results for the product idea, not exact product pages.")
    header.append("")
    body = [format_match(match, index + 1) for index, match in enumerate(report.matches)]
    return "\n\n".join(header + body)


def compose_keyword_report(result: KeywordCommandResult) -> str:
    header = [
        f"Keyword: {result.keyword.term}",
        f"Trend score: {result.keyword.trend_score}",
        f"Оценочный volume: {result.keyword.estimated_volume}",
        f"Keyword difficulty: {result.keyword.difficulty if result.keyword.difficulty is not None else 'н/д'}",
    ]
    if result.note and not result.matches:
        return "\n".join(header + ["", result.note])

    matches = [format_match(match, index + 1) for index, match in enumerate(result.matches)]
    if result.note:
        matches.append(result.note)
    return "\n\n".join(["\n".join(header)] + matches)


def format_match(match: ProductKeywordMatch, index: int) -> str:
    suggestions = "\n".join(f"- {item}" for item in match.seo_suggestions)
    price = f"${match.product.price:.2f}" if match.product.price is not None else "н/д"
    id_label = "Seed ID" if match.product.asin.startswith("SEED") else "ASIN"
    url_label = "Search URL" if "/s?k=" in match.product.url else "URL"
    return (
        f"{index}. {match.product.title}\n"
        f"{id_label}: {match.product.asin}\n"
        f"Категория: {match.product.category}\n"
        f"Цена: {price}\n"
        f"Оценка спроса: {match.product.estimated_sales}\n"
        f"Keyword: {match.keyword.term}\n"
        f"Keyword volume: {match.keyword.estimated_volume}\n"
        f"Keyword difficulty: {match.keyword.difficulty if match.keyword.difficulty is not None else 'н/д'}\n"
        f"SEO suggestions:\n{suggestions}\n"
        f"{url_label}: {match.product.url}"
    )
