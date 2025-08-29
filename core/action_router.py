# بالا:
from typing import Dict
# + از مرحله قبل:
# from nora.core.usecases.reading_light import ReadingLightUsecase  # تزریق از app.py انجام می‌شود

class ActionRouter:
    def __init__(self, state_store, lighting_uc, audio_uc, reading_light_uc, back_light_uc):
        self.state_store = state_store
        self.lighting = lighting_uc
        self.audio = audio_uc
        self.reading_light = reading_light_uc
        self.back_light = back_light_uc

    def handle(self, source: str, action: str, payload: Dict, corr_id: str = "") -> Dict:
        patch = {}

        # --- Lighting (قدیمی) ---
        if action == "lighting.set":
            patch = self.lighting.set_zone(
                zone=payload.get("zone","under_sofa"),
                mode=payload.get("mode","off"),
                color=payload.get("color","#FFFFFF"),
                brightness=int(payload.get("brightness",128))
            )

        # --- Audio (قدیمی) ---
        elif action == "audio.set_source":
            patch = self.audio.set_source(payload.get("source","bt"))
        elif action == "audio.command":
            patch = self.audio.command(payload.get("op","play_pause"))
        elif action == "audio.set_volume":
            patch = self.audio.set_volume(int(payload.get("volume",70)))

        # --- Reading Light (جدید) ---
        elif action == "reading_light.set":
            want_on = bool(payload.get("on"))
            patch = self.reading_light.set(want_on)

        elif action == "reading_light.toggle":
            # از state فعلی بخوانیم:
            current = self.state_store.get_state()
            current_on = bool(current.get("lighting", {}).get("reading_light", {}).get("on", False))
            patch = self.reading_light.toggle(current_on)

        # --- Back Light (جدید) ---
        elif action == "back_light.set":
            want_on = bool(payload.get("on"))
            patch = self.back_light.set(want_on)

        elif action == "back_light.toggle":
            # از state فعلی بخوانیم:
            current = self.state_store.get_state()
            current_on = bool(current.get("lighting", {}).get("back_light", {}).get("on", False))
            patch = self.back_light.toggle(current_on)
        
        # --- Default ---
        else:
            patch = {}

        if patch:
            return self.state_store.apply_patch(
                patch, source=source, action=action, payload=payload, corr_id=corr_id
            )
        else:
            return self.state_store.get_state()
