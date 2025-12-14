from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from activity import ChatActivityTracker
from status_service import MinecraftMonitor, ServerSnapshot


router = Router()


def format_snapshot(snapshot: ServerSnapshot) -> str:
    if not snapshot.online:
        return "⚠️ Сервер офлайн."

    motd_line = f"Опис: {snapshot.motd}" if snapshot.motd else None
    players_line = (
        f"Гравців: {snapshot.players_online}/{snapshot.players_max}"
        if snapshot.players_max
        else f"Гравців онлайн: {snapshot.players_online}"
    )
    latency_line = (
        f"Затримка: {round(snapshot.latency_ms, 1)} мс"
        if snapshot.latency_ms is not None
        else None
    )
    names_line = (
        "Зараз на сервері: " + ", ".join(snapshot.player_names)
        if snapshot.player_names
        else "На сервері немає гравців."
    )

    lines = [
        "✅ Сервер онлайн.",
        motd_line,
        f"Версія: {snapshot.version or 'невідомо'}",
        players_line,
        names_line,
        latency_line,
    ]
    return "\n".join([line for line in lines if line])


def setup_handlers(monitor: MinecraftMonitor, activity: ChatActivityTracker) -> Router:
    @router.message(Command("start"))
    async def handle_start(message: Message) -> None:
        if not message.from_user or message.from_user.is_bot:
            return
        activity.record_user_activity()
        await message.answer(
            "Привіт! Я стежу за станом Minecraft сервера.\n"
            "Використовуй /status, щоб отримати поточну інформацію."
        )

    @router.message(Command("status"))
    async def handle_status(message: Message) -> None:
        if message.from_user and not message.from_user.is_bot:
            activity.record_user_activity()

        snapshot = monitor.read_cached_snapshot()
        if snapshot is None:
            snapshot = await monitor.fetch_status()

        if snapshot is None:
            await message.answer("Дані недоступні.")
            return

        response = await message.answer(format_snapshot(snapshot))
        activity.record_bot_message(response.message_id)

    @router.message()
    async def track_any_message(message: Message) -> None:
        # Фиксируем любой трафик в чате, чтобы при следующем уведомлении не затирать историю.
        if message.from_user and not message.from_user.is_bot:
            activity.record_user_activity()

    return router
