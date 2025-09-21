import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

CONFIG_PATH = Path(__file__).parent / "config.json"

DEFAULT_TEMPLATE: Dict[str, Any] = {
    "TOKEN": "",
    "GUILD": 0,
    "VM_CHANNEL_ID": 0,
    "VM_CATEGORY_ID": 0
}

def _create_template(path: Path) -> None:
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(DEFAULT_TEMPLATE, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to create {path}: {e}")
        sys.exit(1)

def _load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Syntax Error JSON in {path}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Reading Error {path}: {e}")
        sys.exit(1)

# Если файла нет — создаём шаблон и просим пользователя заполнить
if not CONFIG_PATH.exists():
    print(f"{CONFIG_PATH} file not found. Creating template...")
    _create_template(CONFIG_PATH)
    print(
        f"File {CONFIG_PATH.name} created. Open and fill with your data:\n"
        '  "TOKEN": "your_token",\n'
        '  "GUILD": 123456789012345678,\n'
        '  "VM_CHANNEL_ID": 123456789012345678,\n'
        '  "VM_CATEGORY_ID": 123456789012345678\n\n'
        "Restart your bot."
    )
    sys.exit(0)

_data = _load_json(CONFIG_PATH)

# TOKEN
TOKEN = os.getenv("DISCORD_TOKEN", _data.get("TOKEN", "")).strip()

# GUILD
_guild_env = os.getenv("GUILD_ID")
if _guild_env is not None:
    try:
        GUILD = int(_guild_env)
    except ValueError:
        print("Variable GUILD_ID must be an integer.")
        sys.exit(1)
else:
    try:
        GUILD = int(_data.get("GUILD", 0))
    except (TypeError, ValueError):
        GUILD = 0

# VM_CHANNEL_ID
_voice_env = os.getenv("VM_CHANNEL_ID")
if _voice_env is not None:
    try:
        VM_CHANNEL_ID = int(_voice_env)
    except ValueError:
        print("Variable VM_CHANNEL_ID must be an integer.")
        sys.exit(1)
else:
    try:
        VM_CHANNEL_ID = int(_data.get("VM_CHANNEL_ID", 0))
    except (TypeError, ValueError):
        VM_CHANNEL_ID = 0

# VM_CATEGORY_ID
_cat_env = os.getenv("VM_CATEGORY_ID")
if _cat_env is not None:
    try:
        VM_CATEGORY_ID = int(_cat_env)
    except ValueError:
        print("Variable VM_CATEGORY_ID must be an integer.")
        sys.exit(1)
else:
    try:
        VM_CATEGORY_ID = int(_data.get("VM_CATEGORY_ID", 0))
    except (TypeError, ValueError):
        VM_CATEGORY_ID = 0

# Проверка что всё заполнено
if not TOKEN or not GUILD or not VM_CHANNEL_ID or not VM_CATEGORY_ID:
    print(
        "Config incomplete.\n"
        f"Check {CONFIG_PATH} and fill with your data:\n"
        '  "TOKEN": "your_token",\n'
        '  "GUILD": 123456789012345678,\n'
        '  "VM_CHANNEL_ID": 123456789012345678,\n'
        '  "VM_CATEGORY_ID": 123456789012345678\n\n'
    )
    sys.exit(1)
