from __future__ import annotations

import logging

from amazon_trends_bot.bot.messages import compose_daily_report

logger = logging.getLogger(__name__)


class DailyReportJob:
    def __init__(self, bot, report_service, settings) -> None:
        self.bot = bot
        self.report_service = report_service
        self.settings = settings

    async def run(self) -> None:
        if not self.settings.daily_chat_id:
            logger.warning("DAILY_CHAT_ID is empty. Daily job skipped.")
            return
        report = await self.report_service.generate_daily_report(force_refresh=True)
        await self.bot.send_message(
            chat_id=self.settings.daily_chat_id,
            text=compose_daily_report(report, self.settings),
        )

