import os
import subprocess


# import subprocess, json
# from typing import Dict

# # فرض: raspotify/librespot اجراست و via MPRIS با playerctl قابل کنترل است
# # برای BT: کنترل پخش سمت گوشی است؛ ولوم/میکس از سیستم.

# class AudioService:
#     def __init__(self):
#         self._source = "bt"  # bt | spotify
#         self._volume = 70

#     def _playerctl(self, *args) -> str:
#         try:
#             out = subprocess.check_output(["playerctl", "-p", "librespot", *args], stderr=subprocess.DEVNULL)
#             return out.decode().strip()
#         except Exception:
#             return ""

#     def set_source(self, source: str):
#         if source in ("bt","spotify"):
#             self._source = source
#             # Optional: mute/ducking logic بین منابع

#     def play_pause(self):
#         if self._source == "spotify":
#             self._playerctl("play-pause")

#     def next_track(self):
#         if self._source == "spotify":
#             self._playerctl("next")

#     def prev_track(self):
#         if self._source == "spotify":
#             self._playerctl("previous")

#     def set_volume(self, vol: int):
#         vol = max(0, min(100, vol))
#         self._volume = vol
#         # PipeWire/Pulse کنترل ولوم سیستم (نمونه ساده با pactl):
#         try:
#             subprocess.run(["pactl","set-sink-volume","@DEFAULT_SINK@", f"{vol}%"], check=False)
#         except Exception:
#             pass

#     def status(self) -> Dict:
#         title = artist = ""
#         state = "stopped"
#         if self._source == "spotify":
#             title = self._playerctl("metadata","--format","{{title}}")
#             artist = self._playerctl("metadata","--format","{{artist}}")
#             s = self._playerctl("status")
#             state = s.lower() if s else "stopped"
#         return {
#             "source": self._source,
#             "state": state,
#             "title": title or "",
#             "artist": artist or "",
#             "position": 0,
#             "duration": 0,
#             "volume": self._volume
#         }
    
MOCK = os.environ.get("NORA_MOCK") == "1"

class AudioService:
    def __init__(self):
        self._source = "bt"
        self._volume = 70
        self._mock_state = "stopped"
        self._title = "Test Track"
        self._artist = "Nora Mock"

    def _playerctl(self, *args) -> str:
        if MOCK:
            # شبیه‌سازی پاسخ
            if args[:1] == ("status",):
                return self._mock_state.capitalize()
            if "metadata" in args:
                if "title" in args[-1]: return self._title
                if "artist" in args[-1]: return self._artist
            return ""
        try:
            out = subprocess.check_output(["playerctl", "-p", "librespot", *args], stderr=subprocess.DEVNULL)
            return out.decode().strip()
        except Exception:
            return ""

    def set_source(self, source: str):
        if source in ("bt","spotify"):
            self._source = source

    def play_pause(self):
        if MOCK:
            self._mock_state = "playing" if self._mock_state != "playing" else "paused"
            return
        if self._source == "spotify": self._playerctl("play-pause")

    def next_track(self):
        if MOCK:
            self._title = "Next Test"
            self._artist = "Nora Mock"
            self._mock_state = "playing"
            return
        if self._source == "spotify": self._playerctl("next")

    def prev_track(self):
        if MOCK:
            self._title = "Prev Test"
            self._artist = "Nora Mock"
            self._mock_state = "playing"
            return
        if self._source == "spotify": self._playerctl("previous")

    def set_volume(self, vol: int):
        vol = max(0, min(100, vol))
        self._volume = vol
        if not MOCK:
            try:
                subprocess.run(["pactl","set-sink-volume","@DEFAULT_SINK@", f"{vol}%"], check=False)
            except Exception:
                pass

    def status(self) -> dict:
        if MOCK:
            return {"source": self._source, "state": self._mock_state,
                    "title": self._title, "artist": self._artist,
                    "position": 0, "duration": 0, "volume": self._volume}
        title = self._playerctl("metadata","--format","{{title}}")
        artist = self._playerctl("metadata","--format","{{artist}}")
        s = self._playerctl("status")
        state = s.lower() if s else "stopped"
        return {"source": self._source, "state": state,
                "title": title or "", "artist": artist or "",
                "position": 0, "duration": 0, "volume": self._volume}