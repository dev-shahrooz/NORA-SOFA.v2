# nora/core/state_store.py

import json, sqlite3, threading
from typing import Any, Dict, Optional

SCHEMA_VERSION = "nora/1.1.0"

INIT_SQL = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS state_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts DATETIME DEFAULT CURRENT_TIMESTAMP,
  version TEXT,
  state_json TEXT
);
CREATE TABLE IF NOT EXISTS event_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts DATETIME DEFAULT CURRENT_TIMESTAMP,
  source TEXT,
  action TEXT,
  payload TEXT,
  result TEXT,
  corr_id TEXT
);
"""

DEFAULT_STATE = {
    "schema": SCHEMA_VERSION,
    "lighting": {
        "under_sofa": {"mode": "off", "color": "#FFFFFF", "brightness": "mid"},
        "box": {"mode": "off", "color": "#FFFFFF", "brightness": "mid"},
        "reading_light": {"on": False},  # ← جدید
    },
    "mode": "normal",
    "wifi": {"on": True, "connected": False, "ssid": "", "saved_networks": []},
    "bluetooth": {"on": True},
    "audio": {"volume": 50, "muted": False},
    "player": {"status": "Unknown", "title": "", "artist": ""},
    "lang": "en",
    "clock": {"time": "00:00:00"},
}


class StateStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._lock = threading.RLock()
        with sqlite3.connect(self.db_path) as con:
            con.executescript(INIT_SQL)
            if self._latest_snapshot(con) is None:
                self._write_snapshot(con, DEFAULT_STATE)

    def _latest_snapshot(self, con) -> Optional[Dict[str, Any]]:
        cur = con.execute("SELECT state_json FROM state_snapshots ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        return json.loads(row[0]) if row else None

    def _write_snapshot(self, con, state: Dict[str, Any]):
        con.execute("INSERT INTO state_snapshots(version, state_json) VALUES (?,?)", (
            state.get("schema", SCHEMA_VERSION), json.dumps(state)
        ))

    def get_state(self) -> Dict[str, Any]:
        with self._lock, sqlite3.connect(self.db_path) as con:
            s = self._latest_snapshot(con) or DEFAULT_STATE.copy()
            s.setdefault("lighting", {})
            s["lighting"].setdefault("reading_light", {"on": False})
            s["lighting"].setdefault("back_light", {"on": False})
            s.setdefault("schema", SCHEMA_VERSION)
            s.setdefault("mode", "normal")
            s.setdefault("bluetooth", {"on": True})
            s.setdefault("wifi", {})
            s["wifi"].setdefault("on", True)
            s["wifi"].setdefault("connected", False)
            s["wifi"].setdefault("ssid", "")
            s["wifi"].setdefault("saved_networks", [])
            s["wifi"].setdefault("last_connection_attempt", None)
            s.setdefault("audio", {})
            s["audio"].setdefault("volume", 50)
            s["audio"].setdefault("muted", False)
            s.setdefault("player", {})
            s["player"].setdefault("status", "Unknown")
            s["player"].setdefault("title", "")
            s["player"].setdefault("artist", "")
            s.setdefault("lang", "en")
            s.setdefault("clock", {})
            s["clock"].setdefault("time", "00:00:00")
            s.setdefault("voice_assistant", {})
            s["voice_assistant"].setdefault("wake_word_enabled", True)

            return s

    def apply_patch(self, patch: Dict[str, Any], source: str, action: str, payload: Dict[str, Any], corr_id: str = "") -> Dict[str, Any]:
        with self._lock, sqlite3.connect(self.db_path) as con:
            state = self._latest_snapshot(con) or DEFAULT_STATE.copy()
            # Merge shallow for this scaffold (می‌توان عمقی پیاده کرد)
            for k, v in patch.items():
                if isinstance(v, dict) and isinstance(state.get(k), dict):
                    state[k].update(v)
                else:
                    state[k] = v
            self._write_snapshot(con, state)
            con.execute("INSERT INTO event_log(source,action,payload,result,corr_id) VALUES (?,?,?,?,?)",
                        (source, action, json.dumps(payload), json.dumps(patch), corr_id))
            return state
