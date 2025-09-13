import os
import subprocess

MOCK = os.environ.get("NORA_MOCK") == "1"
    
play = ["playerctl", "play"]
pause = ["playerctl", "pause"]

class PlayerService:
    """Control media playback via playerctl."""

    def _run(self, *args):
        if MOCK:
            return
        try:
            subprocess.run(["playerctl", *args], check=False,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def play(self):
        # self._run("play")
        subprocess.run(play, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


    def pause(self):
        # self._run("pause")
        subprocess.run(pause, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


    def next(self):
        self._run("next")

    def previous(self):
        self._run("previous")

    def status(self) -> str:
        if MOCK:
            return "Stopped"
        try:
            out = subprocess.check_output(["playerctl", "status"], text=True).strip()
            return out
        except Exception:
            return "Unknown"

    def metadata(self) -> dict:
        if MOCK:
            return {"title": "", "artist": ""}
        title = ""
        artist = ""
        try:
            title = subprocess.check_output([
                "playerctl", "metadata", "title"
            ], text=True).strip()
        except Exception:
            pass
        try:
            artist = subprocess.check_output([
                "playerctl", "metadata", "artist"
            ], text=True).strip()
        except Exception:
            pass
        return {"title": title, "artist": artist}
