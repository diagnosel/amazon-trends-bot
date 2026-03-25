from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart

from amazon_trends_bot.bot.keyboards import build_main_keyboard
from amazon_trends_bot.bot.messages import (
    compose_daily_report,
    compose_keyword_report,
    compose_start_message,
)
from amazon_trends_bot.services.keyword_service import BrandedKeywordError, KeywordValidationError

logger = logging.getLogger(__name__)


class BotHandlers:
    def __init__(self, report_service, settings) -> None:
        self.report_service = report_service
        self.settings = settings

    def build_router(self) -> Router:
        router = Router()
        router.message.register(self.handle_start, CommandStart())
        router.message.register(self.handle_daily, Command("daily"))
        router.message.register(self.handle_keyword, Command("keyword"))
        return router

    async def handle_start(self, message) -> None:
        await message.answer(
            compose_start_message(self.settings),
            reply_markup=build_main_keyboard(),
        )

    async def handle_daily(self, message) -> None:
        try:
            report = await self.report_service.get_daily_report()
            await message.answer(
                compose_daily_report(report, self.settings),
                reply_markup=build_main_keyboard(),
            )
        except Exception as exc:
            logger.exception("Daily handler failed: %s", exc)
            await message.answer(
                "Не удалось собрать daily-отчёт. Попробуйте ещё раз чуть позже.",
                reply_markup=build_main_keyboard(),
            )

    async def handle_keyword(self, message, command: CommandObject | None = None) -> None:
        term = (command.args if command and command.args else "").strip()
        if not term:
            await message.answer(
                "Нужно передать keyword. Пример: /keyword portable blender",
                reply_markup=build_main_keyboard(),
            )
            return

        try:
            result = await self.report_service.analyze_keyword(term)
            await message.answer(
                compose_keyword_report(result),
                reply_markup=build_main_keyboard(),
            )
        except BrandedKeywordError:
            await message.answer(
                "Этот запрос выглядит брендовым. Попробуйте более общий небрендовый keyword.",
                reply_markup=build_main_keyboard(),
            )
        except KeywordValidationError:
            await message.answer(
                "Не получилось разобрать keyword. Попробуйте запрос из 2-4 слов.",
                reply_markup=build_main_keyboard(),
            )
        except Exception as exc:
            logger.exception("Keyword handler failed: %s", exc)
            await message.answer(
                "Не удалось обработать keyword прямо сейчас. Попробуйте позже.",
                reply_markup=build_main_keyboard(),
            )
