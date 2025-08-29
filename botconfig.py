# config.py
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

CONFIG_PATH = Path(__file__).parent / "config.json"

DEFAULT_TEMPLATE: Dict[str, Any] = {
    "TOKEN": "",
    "GUILD": 0
}

def _create_template(path: Path) -> None:
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(DEFAULT_TEMPLATE, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Не удалось создать {path}: {e}")
        sys.exit(1)

def _load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Ошибка синтаксиса JSON в {path}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при чтении {path}: {e}")
        sys.exit(1)

# Если файла нет — создаём шаблон и просим заполнить
if not CONFIG_PATH.exists():
    print(f"{CONFIG_PATH} не найден. Создаю шаблон...")
    _create_template(CONFIG_PATH)
    print(
        f"Файл {CONFIG_PATH.name} создан. Открой его и заполни поля:\n"
        '  "TOKEN": "тут_токен_бота",\n'
        '  "GUILD": 123456789012345678\n\n'
        "После заполнения перезапусти бота."
    )
    # Чтобы бот не запустился с пустой конфигурацией — завершаем программу
    sys.exit(0)

_data = _load_json(CONFIG_PATH)

# Позволяем для гибкости переопределять через переменные окружения
TOKEN = os.getenv("DISCORD_TOKEN", _data.get("TOKEN", "")).strip()
# GUILD может быть передан в окружении как строка — пробуем привести к int
_guild_env = os.getenv("GUILD_ID")
if _guild_env is not None:
    try:
        GUILD = int(_guild_env)
    except ValueError:
        print("Переменная окружения GUILD_ID должна быть числом (id гильдии).")
        sys.exit(1)
else:
    # читаем из файла; если что-то не так — установим 0 и дальше проверим
    try:
        GUILD = int(_data.get("GUILD", 0))
    except (TypeError, ValueError):
        GUILD = 0

# Проверяем на валидность — если токен пустой или guld == 0 -> просим заполнить и выходим
if not TOKEN or not GUILD:
    print(
        "Конфигурация неполная.\n"
        f"Проверь {CONFIG_PATH} и заполните поля:\n"
        '  "TOKEN": "тут_токен_бота",\n'
        '  "GUILD": 123456789012345678\n\n'
        "Альтернатива: используй переменные окружения DISCORD_TOKEN и GUILD_ID."
    )
    sys.exit(1)
