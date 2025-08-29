# nora/core/usecases/audio.py
from typing import Dict
from services.audio_service import AudioService

class AudioUsecase:
    def __init__(self, audio: AudioService):
        self.audio = audio

    def set_source(self, source: str) -> Dict:
        self.audio.set_source(source)
        st = self.audio.status()
        return {"audio": st}

    def command(self, op: str) -> Dict:
        if op == "play_pause":
            self.audio.play_pause()
        elif op == "next":
            self.audio.next_track()
        elif op == "prev":
            self.audio.prev_track()
        st = self.audio.status()
        return {"audio": st}

    def set_volume(self, vol: int) -> Dict:
        self.audio.set_volume(vol)
        st = self.audio.status()
        return {"audio": st}