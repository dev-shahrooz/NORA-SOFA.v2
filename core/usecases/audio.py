from typing import Dict
from services.audio_service import AudioService


class AudioUsecase:
    """Usecase for controlling system volume."""

    def __init__(self, svc: AudioService):
        self.svc = svc

    def set_volume(self, volume: int) -> Dict:
        volume = max(0, min(100, int(volume)))
        self.svc.set_volume(volume)
        current = self.svc.get_volume()
        return {"audio": {"volume": current}}