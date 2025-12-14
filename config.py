import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class Settings:
    telegram_bot_token: str
    telegram_chat_id: int
    minecraft_host: str
    minecraft_port: int
    poll_interval_seconds: int
    status_file_path: str
    request_timeout_seconds: int
    offline_after_failures: int


def load_settings() -> Settings:
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    host = os.getenv("MINECRAFT_HOST")
    port = os.getenv("MINECRAFT_PORT", "25565")
    interval = os.getenv("POLL_INTERVAL_SECONDS", "30")
    status_file_path = os.getenv("STATUS_FILE_PATH", "data/status.json")
    request_timeout = os.getenv("REQUEST_TIMEOUT_SECONDS", "5")
    offline_after_failures = os.getenv("OFFLINE_AFTER_FAILURES", "2")

    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")
    if not chat_id:
        raise RuntimeError("TELEGRAM_CHAT_ID is required")
    if not host:
        raise RuntimeError("MINECRAFT_HOST is required")

    try:
        parsed_port = int(port)
    except ValueError as exc:
        raise RuntimeError("MINECRAFT_PORT must be an integer") from exc

    try:
        parsed_interval = int(interval)
    except ValueError as exc:
        raise RuntimeError("POLL_INTERVAL_SECONDS must be an integer") from exc

    try:
        parsed_timeout = int(request_timeout)
    except ValueError as exc:
        raise RuntimeError("REQUEST_TIMEOUT_SECONDS must be an integer") from exc

    try:
        parsed_offline_after = int(offline_after_failures)
    except ValueError as exc:
        raise RuntimeError("OFFLINE_AFTER_FAILURES must be an integer") from exc

    return Settings(
        telegram_bot_token=token,
        telegram_chat_id=int(chat_id),
        minecraft_host=host,
        minecraft_port=parsed_port,
        poll_interval_seconds=parsed_interval,
        status_file_path=status_file_path,
        request_timeout_seconds=parsed_timeout,
        offline_after_failures=parsed_offline_after,
    )
