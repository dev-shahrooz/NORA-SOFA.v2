from typing import Dict
from services.audio_service import AudioService


class AudioUsecase:
    """Usecase for controlling system volume and mute state."""

    def __init__(self, svc: AudioService, esp_link, state_store):
        self.svc = svc
        self.esp = esp_link
        self.state_store = state_store

    def set_volume(self, volume: int) -> Dict:
        volume = max(0, min(100, int(volume)))
        print("audio.py")
        print(volume)
        self.svc.set_volume(volume)
        return {"audio": {"volume": volume}}

    def set_mute(self, mute: bool) -> Dict:
        if mute:
            self.esp.send_command("NORA_sound_OFF")
        else:
            mode = self.state_store.get_state().get("mode", "normal")
            if mode == "party":
                self.esp.send_command("NORA_sound_BOOST")
            else:
                self.esp.send_command("NORA_sound_ON")
        return {"audio": {"muted": bool(mute)}}