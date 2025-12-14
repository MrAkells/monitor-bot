import asyncio
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from aiogram import Bot
from mcstatus import JavaServer
from activity import ChatActivityTracker


@dataclass
class ServerSnapshot:
    online: bool
    motd: Optional[str]
    version: Optional[str]
    latency_ms: Optional[float]
    players_online: int
    players_max: int
    player_names: list[str] = field(default_factory=list)
    last_updated: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return asdict(self)


class MinecraftMonitor:
    def __init__(
        self,
        host: str,
        port: int,
        status_file: Path,
        poll_interval_seconds: int,
        activity: ChatActivityTracker,
    ) -> None:
        self.server = JavaServer(host, port=port)
        self.status_file = status_file
        self.poll_interval_seconds = poll_interval_seconds
        self._previous_snapshot: Optional[ServerSnapshot] = None
        self.activity = activity

    async def fetch_status(self) -> ServerSnapshot:
        try:
            response = await self.server.async_status()
            motd = getattr(response.description, "to_plain", lambda: None)()
            player_names = [player.name for player in response.players.sample or []]
            return ServerSnapshot(
                online=True,
                motd=motd,
                version=response.version.name,
                latency_ms=response.latency,
                players_online=response.players.online,
                players_max=response.players.max,
                player_names=player_names,
            )
        except Exception:
            # Treat any exception as offline state but keep last known data safe.
            return ServerSnapshot(
                online=False,
                motd=None,
                version=None,
                latency_ms=None,
                players_online=0,
                players_max=0,
                player_names=[],
            )

    def _write_snapshot(self, snapshot: ServerSnapshot) -> None:
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        with self.status_file.open("w", encoding="utf-8") as fp:
            json.dump(
                {
                    "source": "monitor-bot",
                    "status": snapshot.to_dict(),
                },
                fp,
                ensure_ascii=False,
                indent=2,
            )

    def read_cached_snapshot(self) -> Optional[ServerSnapshot]:
        if not self.status_file.exists():
            return None

        try:
            with self.status_file.open("r", encoding="utf-8") as fp:
                payload = json.load(fp)
        except (json.JSONDecodeError, OSError):
            return None

        status = payload.get("status") if isinstance(payload, dict) else None
        if not isinstance(status, dict):
            return None

        try:
            return ServerSnapshot(
                online=bool(status.get("online")),
                motd=status.get("motd"),
                version=status.get("version"),
                latency_ms=status.get("latency_ms"),
                players_online=int(status.get("players_online", 0)),
                players_max=int(status.get("players_max", 0)),
                player_names=list(status.get("player_names", [])),
                last_updated=status.get("last_updated")
                or datetime.now(timezone.utc).isoformat(),
            )
        except Exception:
            return None

    def _build_notification(self, snapshot: ServerSnapshot) -> Optional[str]:
        previous = self._previous_snapshot
        self._previous_snapshot = snapshot

        if previous is None:
            prefix = "Старт моніторингу."
            return f"✅ {prefix} Сервер онлайн." if snapshot.online else f"⚠️ {prefix} Сервер офлайн."

        if previous.online != snapshot.online:
            return "✅ Сервер знову онлайн." if snapshot.online else "⚠️ Сервер офлайн."

        return None

    async def _send_or_edit(self, bot: Bot, chat_id: int, text: str) -> None:
        """Edit last bot message if нет новых сообщений в чате, иначе отправить новое."""
        if self.activity.can_edit_last_bot_message():
            message_id = self.activity.last_bot_message_id
            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=text,
                )
                if message_id is not None:
                    self.activity.record_bot_message(message_id)
                return
            except Exception:
                # Если не получилось отредактировать (удалено/старое), отправим новое.
                pass

        message = await bot.send_message(chat_id=chat_id, text=text)
        self.activity.record_bot_message(message.message_id)

    async def run(self, bot: Bot, chat_id: int) -> None:
        while True:
            snapshot = await self.fetch_status()
            self._write_snapshot(snapshot)

            message = self._build_notification(snapshot)
            if message:
                try:
                    await self._send_or_edit(bot, chat_id, message)
                except Exception:
                    # Ignore send failures and try again in the next iteration.
                    pass

            await asyncio.sleep(self.poll_interval_seconds)
