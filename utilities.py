import json
import os
from threading import Lock
from typing import Any
import sqlite3

class JsonWorker:
    def __init__(self, json_path: str):
        super().__setattr__("json_path", json_path)
        super().__setattr__("_data", self._open_data())

    def _open_data(self) -> dict[str, Any]:
        os.makedirs(os.path.dirname(self.json_path) or ".", exist_ok=True)

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=4)
            return {}

    def _commit_data(self) -> None:
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=4)

class DataWorker(JsonWorker):
    def __getattr__(self, name: str) -> Any:
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any):
        if name in {"json_path", "_data"}:
            super().__setattr__(name, value)
            return

        self._data[name] = value
        self._commit_data()


class BridgeStorage:
    """
    Storage manager for the bridge between Discord and Telegram.
    Handles JSON queues and linked message mappings.
    """

    def __init__(self,
                 link_path="modules/Bridge/LinkMess.json",
                 req_path="modules/Bridge/queues/Requests.json",
                 dtt_path="modules/Bridge/queues/DisToTel.json",
                 ttd_path="modules/Bridge/queues/TelToDis.json"):

        self.req_path = req_path
        self.link_path = link_path
        self.dtt_path = dtt_path
        self.ttd_path = ttd_path

        # Locks to ensure thread-safe access to each JSON file
        self._req_lock = Lock()
        self._link_lock = Lock()
        self._dtt_lock = Lock()
        self._ttd_lock = Lock()

    # -------------------------
    # Internal JSON operations
    # -------------------------

    @staticmethod
    def _load_json(path: str) -> list:
        """
        Safely load JSON data from a file as a list.
        - If file does not exist, creates it as an empty list.
        - If JSON is invalid or any error occurs, returns an empty list.
        """
        # Create a directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # If the file does not exist, we create an empty JSON
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            return []

        # Trying to load JSON
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return []

    @staticmethod
    def _save_json(path: str, data: list):
        """Save list to JSON file. Directories are created automatically."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # -------------------------
    # Request queue operations
    # -------------------------

    def load_req(self) -> list:
        with self._req_lock:
            return self._load_json(self.req_path)

    def save_req(self, data: list):
        with self._req_lock:
            self._save_json(self.req_path, data)

    def add_req(self, element):
        data = self.load_req()
        data.append(element)
        self.save_req(data)

    def pop_req(self, mode):
        """Pop first request where request['way'] == mode."""
        data = self.load_req()
        found = None

        for item in data:
            if item.get("way") == mode:
                found = item
                data.remove(item)
                break

        self.save_req(data)
        return found

    # -------------------------
    # Linked message table
    # -------------------------

    def load_link(self) -> list:
        with self._link_lock:
            return self._load_json(self.link_path)

    def save_link(self, data: list):
        with self._link_lock:
            self._save_json(self.link_path, data)

    def add_link(self, element):
        """Store message link pair (Discord ↔ Telegram). Auto-truncate to 5000 entries."""
        data = self.load_link()
        if len(data) >= 5000:
            data.pop(0)
        data.append(element)
        self.save_link(data)

    def clear_link(self):
        self.save_link([])

    # -------------------------
    # Discord → Telegram queue
    # -------------------------

    def load_dtt(self) -> list:
        with self._dtt_lock:
            return self._load_json(self.dtt_path)

    def save_dtt(self, data: list):
        with self._dtt_lock:
            self._save_json(self.dtt_path, data)

    def add_dtt(self, element):
        data = self.load_dtt()
        data.append(element)
        self.save_dtt(data)

    def pop_dtt(self):
        data = self.load_dtt()
        if not data:
            return None
        element = data.pop(0)
        self.save_dtt(data)
        return element

    # -------------------------
    # Telegram → Discord queue
    # -------------------------

    def load_ttd(self) -> list:
        with self._ttd_lock:
            return self._load_json(self.ttd_path)

    def save_ttd(self, data: list):
        with self._ttd_lock:
            self._save_json(self.ttd_path, data)

    def add_ttd(self, element):
        data = self.load_ttd()
        data.append(element)
        self.save_ttd(data)

    def pop_ttd(self):
        data = self.load_ttd()
        if not data:
            return None
        element = data.pop(0)
        self.save_ttd(data)
        return element

storage = BridgeStorage()


class Database:
    def __init__(self, path: str) -> None:
        self._con = sqlite3.connect(path)
        self._con.row_factory = sqlite3.Row
        self._con.execute("PRAGMA foreign_keys = ON")

    def close_(self) -> None:
        self._con.close()

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> sqlite3.Cursor:
        return self._con.execute(query, params)

    def transaction(self):
        return self._con
