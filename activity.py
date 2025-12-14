from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ChatActivityTracker:
    last_bot_message_id: Optional[int] = None
    last_bot_message_time: Optional[datetime] = None
    last_user_message_time: Optional[datetime] = None
    _now_fn: callable = field(default=_now, repr=False)

    def record_user_activity(self) -> None:
        self.last_user_message_time = self._now_fn()

    def record_bot_message(self, message_id: int) -> None:
        self.last_bot_message_id = message_id
        self.last_bot_message_time = self._now_fn()

    def can_edit_last_bot_message(self) -> bool:
        if self.last_bot_message_id is None:
            return False
        if self.last_user_message_time is None:
            return True
        if self.last_bot_message_time is None:
            return False
        # Edit only if после последнего бот-сообщения не было новых сообщений пользователей.
        return self.last_bot_message_time >= self.last_user_message_time
