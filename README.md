# Telegram Minecraft Monitor Bot

Бот на `aiogram`, що регулярно перевіряє статус Minecraft сервера і:
- Надсилає сповіщення в Telegram чат (онлайн/офлайн).
- Записує актуальний стан у `status.json`, щоб дані можна було підхопити на сайт.

## Швидкий старт
1) Встановіть залежності:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2) Заповніть `.env` (див. приклад у `.env.example`):
```
TELEGRAM_BOT_TOKEN=ваш_токен
TELEGRAM_CHAT_ID=chat_id_куди_слати_сповіщення
MINECRAFT_HOST=example.org
MINECRAFT_PORT=25565
POLL_INTERVAL_SECONDS=30
STATUS_FILE_PATH=data/status.json
REQUEST_TIMEOUT_SECONDS=5
OFFLINE_AFTER_FAILURES=2
```
3) Запустіть бота:
```bash
python main.py
```

## Запуск у Docker
1) Зібрати образ:
```bash
docker build -t monitor-bot .
```
2) Запустити, передавши змінні оточення:
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
`STATUS_FILE_PATH` варто вказувати у змонтовану директорію (`/data`), щоб JSON був доступний зовні.

## Запуск через Docker Compose
1) Заповніть `.env` (TOKEN, CHAT_ID, HOST тощо). `STATUS_FILE_PATH` можна залишити як `/data/status.json` — він задається в `docker-compose.yml`.
2) Запустіть:
```bash
docker-compose up -d
```
3) Дані будуть у локальній директорії `./data/status.json` (проксі на `/data` у контейнері).

## Що робить бот
- Кожні `POLL_INTERVAL_SECONDS` секунд опитує Minecraft сервер.
- Пише результат у JSON файл `STATUS_FILE_PATH`, наприклад `data/status.json`:
```json
{
  "source": "monitor-bot",
  "status": {
    "online": true,
    "motd": "Привіт!",
    "version": "1.20.4",
    "latency_ms": 62.5,
    "players_online": 3,
    "players_max": 20,
    "player_names": ["Steve", "Alex"],
    "last_updated": "2024-01-01T12:00:00.000000+00:00"
  }
}
```
- Надсилає сповіщення лише про зміну статусу (онлайн/офлайн).
- Команда `/status` у чаті показує актуальну інформацію (береться з файлу, якщо його нема — запитує напряму).

## Дані для сайту
- Забирайте файл `STATUS_FILE_PATH` у зручний спосіб (наприклад, віддавайте вебсервером або читайте напряму з файлової системи) — структура стабільна.
- Поле `last_updated` у форматі ISO 8601 допоможе відображати час оновлення.

## Налаштування
- Усі параметри задаються через змінні оточення (див. `.env.example`).
- `POLL_INTERVAL_SECONDS` — частота опитування.
- `STATUS_FILE_PATH` — куди писати JSON. Скрипт сам створить директорію, якщо її немає.
- `REQUEST_TIMEOUT_SECONDS` — таймаут запиту до сервера (щоб не ловити «вічний» конект).
- `OFFLINE_AFTER_FAILURES` — скільки послідовних помилок/таймаутів вважати перед тим, як оголосити офлайн.

## Перевірка
- Запустіть бота і в Telegram відправте `/start`, потім `/status`, щоб побачити поточні дані.
- У каталозі `STATUS_FILE_PATH` має з’явитися актуальний `status.json`.
