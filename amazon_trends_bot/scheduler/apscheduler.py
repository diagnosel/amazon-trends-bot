from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo

from amazon_trends_bot.scheduler.daily_job import DailyReportJob


class BotScheduler:
    def __init__(self, bot, report_service, settings) -> None:
        self.bot = bot
        self.report_service = report_service
        self.settings = settings
        self.scheduler = AsyncIOScheduler(timezone=ZoneInfo(settings.timezone))

    def start(self) -> None:
        if not self.settings.daily_chat_id:
            return
        job = DailyReportJob(self.bot, self.report_service, self.settings)
        self.scheduler.add_job(
            job.run,
            CronTrigger(hour=self.settings.daily_hour, minute=self.settings.daily_minute),
            id="daily_report",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
            misfire_grace_time=60 * 30,
        )
        self.scheduler.start()

    async def stop(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

