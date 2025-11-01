import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Type

CONFIG_PATH = Path(__file__).parent / "config.json"

# Config template
DEFAULT_TEMPLATE: Dict[str, Any] = {
    "TOKEN": "",
    "GUILD": 0,
    "VM_CHANNEL_ID": 0,
    "VM_CATEGORY_ID": 0,
    "LOG_CHANNEL_ID": 0,
}

# data types
EXPECTED_TYPES: Dict[str, Type] = {
    "TOKEN": str,
    "GUILD": int,
    "VM_CHANNEL_ID": int,
    "VM_CATEGORY_ID": int,
    "LOG_CHANNEL_ID": int,
}


class Config:

    def __init__(self, path: Path):
        self.path = path
        data = self._load_and_merge()

        for key, value in data.items():
            setattr(self, key, self._get_value(key, value))

        self._validate()

    # ====== Helper methods ======

    def _load_and_merge(self) -> Dict[str, Any]:
        """Loads JSON, creates it if missing, fills in missing keys."""
        try:
            with self.path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"{self.path.name} not found. Creating template...")
            self._create_template()
            sys.exit(0)
        except json.JSONDecodeError as e:
            print(f"JSON syntax error in {self.path.name}: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading {self.path.name}: {e}")
            sys.exit(1)

        # Add new fields if they appeared in DEFAULT_TEMPLATE
        updated = False
        for key, default_value in DEFAULT_TEMPLATE.items():
            if key not in data:
                data[key] = default_value
                updated = True
        if updated:
            with self.path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Config updated with new default keys.")

        return data

    def _create_template(self) -> None:
        """Creates an empty config.json template."""
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(DEFAULT_TEMPLATE, f, indent=4, ensure_ascii=False)
        print(f"Created {self.path.name}. Fill it with your data and restart the bot.")

    def _get_value(self, key: str, default: Any) -> Any:
        """Takes value from environment first, then from file, with auto-conversion."""
        env_value = os.getenv(key)
        if env_value is not None:
            target_type = EXPECTED_TYPES.get(key, str)
            try:
                return target_type(env_value)
            except ValueError:
                print(f"Invalid type for {key} in environment (expected {target_type.__name__}).")
                sys.exit(1)
        return default

    def _validate(self) -> None:
        """Checks that required fields are not empty."""
        missing = [k for k, v in vars(self).items() if k.isupper() and not v]
        if missing:
            print(f"Config incomplete: {', '.join(missing)}\nFill in {self.path} and restart.")
            sys.exit(1)



config = Config(CONFIG_PATH)
