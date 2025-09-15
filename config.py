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

# If the config file does not exist — create the template and prompt the user to fill it
if not CONFIG_PATH.exists():
    print(f"{CONFIG_PATH} file not found. Creating template...")
    _create_template(CONFIG_PATH)
    print(
        f"File {CONFIG_PATH.name} created. Open and fill with your data:\n"
        '  "TOKEN": "your_token",\n'
        '  "GUILD": 123456789012345678\n\n'
        "Restart your bot."
    )
    # Prevent the bot from running with an empty configuration — exit now
    sys.exit(0)

_data = _load_json(CONFIG_PATH)

# Allow overriding via environment variables for flexibility
TOKEN = os.getenv("DISCORD_TOKEN", _data.get("TOKEN", "")).strip()
# GUILD can be provided via environment as a string — try to convert it to int
_guild_env = os.getenv("GUILD_ID")
if _guild_env is not None:
    try:
        GUILD = int(_guild_env)
    except ValueError:
        print("Variable GUILD_ID need to an integer (guild id).")
        sys.exit(1)
else:
    # Read from the file; if something is wrong set 0 and validate later
    try:
        GUILD = int(_data.get("GUILD", 0))
    except (TypeError, ValueError):
        GUILD = 0

# Validate: if token is empty or GUILD == 0 -> ask to fill the file and exit
if not TOKEN or not GUILD:
    print(
        "Config incomplete data.\n"
        f"Check {CONFIG_PATH} and fill with your data:\n"
        '  "TOKEN": "your_token",\n'
        '  "GUILD": 123456789012345678\n\n'
    )
    sys.exit(1)
