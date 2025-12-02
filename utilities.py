import json
import os
from threading import Lock


class BridgeStorage:
    """
    Storage manager for the bridge between Discord and Telegram.
    Handles JSON queues and linked message mappings.
    """

    def __init__(self,
                 req_path="cogs/Bridge/queues/Requests.json",
                 link_path="cogs/Bridge/LinkMess.json",
                 dtt_path="cogs/Bridge/queues/DisToTel.json",
                 ttd_path="cogs/Bridge/queues/TelToDis.json"):

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
        """Safely load JSON data as list. If file does not exist or is corrupted, return empty list."""
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
        except Exception:  # noqa
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