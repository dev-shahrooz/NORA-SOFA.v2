import os
import subprocess

MOCK = os.environ.get("NORA_MOCK") == "1"

class AudioService:
    """Control system volume via amixer."""

    def __init__(self):
        self._mock_vol = 50

    def set_volume(self, volume: int) -> None:
        volume = max(0, min(100, int(volume)))
        if MOCK:
            self._mock_vol = volume
            return
        rvolume = ["amixer", "sset", "Master", f"{volume}%"]
        try:
            print("audio_service")
            print(rvolume)
            subprocess.run(
                rvolume,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass

    def get_volume(self) -> int:
        if MOCK:
            return self._mock_vol
        try:
            out = subprocess.check_output(["amixer", "sget", "Master"], text=True)
            import re

            m = re.search(r"\[(\d+)%\]", out)
            if m:
                return int(m.group(1))
        except Exception:
            pass
        return 0