# anki-telegram-bot

## Launch bot
- `cp .env.example .env` и заполнить .env
- `docker compose up -d`

## Launch tests
- `uv sync` - установка зависимостей и билд модуля
- `uv pip install -e ".[dev]"` - установка зависимостей для pre-commit и тестов
- `pytest tests/test_handlers.py -v` - запуск тестов хэндлеров
