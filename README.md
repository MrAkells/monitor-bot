# Telegram Minecraft Monitor Bot

Бот на `aiogram` который регулярно проверяет статус Minecraft сервера и:
- Отправляет уведомления в Telegram чат (онлайн/офлайн, изменения игроков).
- Записывает актуальное состояние в `status.json`, чтобы данные можно было забирать на сайт.

## Быстрый старт
1) Установите зависимости:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2) Заполните `.env` (смотрите пример в `.env.example`):
```
TELEGRAM_BOT_TOKEN=ваш_токен
TELEGRAM_CHAT_ID=чат_id_куда_слать_уведомления
MINECRAFT_HOST=example.org
MINECRAFT_PORT=25565
POLL_INTERVAL_SECONDS=30
STATUS_FILE_PATH=data/status.json
```
3) Запустите бота:
```bash
python main.py
```

## Запуск в Docker
1) Собрать образ:
```bash
docker build -t monitor-bot .
```
2) Запустить, передав переменные окружения:
```bash
docker run -d \
  --name monitor-bot \
  -e TELEGRAM_BOT_TOKEN=... \
  -e TELEGRAM_CHAT_ID=... \
  -e MINECRAFT_HOST=example.org \
  -e MINECRAFT_PORT=25565 \
  -e POLL_INTERVAL_SECONDS=30 \
  -e STATUS_FILE_PATH=/data/status.json \
  -v "$(pwd)/data:/data" \
  monitor-bot
```
`STATUS_FILE_PATH` лучше указывать в смонтированную директорию (`/data`), чтобы JSON был доступен снаружи.

## Что делает бот
- Каждые `POLL_INTERVAL_SECONDS` секунд опрашивает сервер Minecraft.
- Пишет результат в JSON файл `STATUS_FILE_PATH`, например `data/status.json`:
```json
{
  "source": "monitor-bot",
  "status": {
    "online": true,
    "motd": "Привет!",
    "version": "1.20.4",
    "latency_ms": 62.5,
    "players_online": 3,
    "players_max": 20,
    "player_names": ["Steve", "Alex"],
    "last_updated": "2024-01-01T12:00:00.000000+00:00"
  }
}
```
- Следит за изменениями и шлет уведомления в чат: сервер упал/поднялся, кто зашел/вышел, текущее число игроков.
- Команда `/status` в чате выводит актуальную информацию (берется из файла, при его отсутствии запрашивается напрямую).

## Использование данных на сайте
- Забирайте файл `STATUS_FILE_PATH` любым удобным способом (например, отдавайте его веб-сервером или читайте напрямую из файловой системы) — структура стабильная.
- Поле `last_updated` в формате ISO 8601 поможет показывать время обновления.

## Настройки
- Все параметры задаются через переменные окружения (см. `.env.example`).
- `POLL_INTERVAL_SECONDS` — частота опроса.
- `STATUS_FILE_PATH` — куда писать JSON. Скрипт сам создаст директорию, если ее нет.

## Проверка
- Запустите бота и в Telegram отправьте `/start`, затем `/status` чтобы увидеть текущие данные.
- В каталоге `STATUS_FILE_PATH` должен появиться актуальный `status.json`.
