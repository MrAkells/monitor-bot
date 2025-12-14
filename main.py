import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from activity import ChatActivityTracker
from bot_handlers import setup_handlers
from config import load_settings
from status_service import MinecraftMonitor


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = load_settings()

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher()

    activity = ChatActivityTracker()

    monitor = MinecraftMonitor(
        host=settings.minecraft_host,
        port=settings.minecraft_port,
        status_file=Path(settings.status_file_path),
        poll_interval_seconds=settings.poll_interval_seconds,
        activity=activity,
    )
    dp.include_router(setup_handlers(monitor, activity))

    # Background task: periodically check server status and push updates.
    asyncio.create_task(monitor.run(bot, settings.telegram_chat_id))

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
