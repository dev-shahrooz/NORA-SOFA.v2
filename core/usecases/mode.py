# nora/core/usecases/mode.py
from typing import Dict, Any
import time

from core.state_store import DEFAULT_STATE


class ModeUsecase:
    """Toggle between normal and party modes using ESP32 for hardware control."""


    def __init__(self, state_store, lighting_uc, reading_light_uc, back_light_uc, esp_link):

        self.state_store = state_store
        self.lighting = lighting_uc
        self.reading_light = reading_light_uc
        self.back_light = back_light_uc
        self.esp = esp_link
        self._saved_state: Dict[str, Any] | None = None
        self._saved_back_light_on: bool | None = None
        
    def _merge(self, base: Dict, update: Dict) -> Dict:
        for k, v in update.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict):
                base[k].update(v)
            else:
                base[k] = v
        return base

    def toggle(self) -> Dict:
        current = self.state_store.get_state()
        patch: Dict[str, Any] = {}

        if current.get("mode") == "party":
            # Return to normal mode
            self.esp.send_command("NORA_box_CLOSE")
            self.esp.send_command("NORA_sound_ON")
            saved = self._saved_state or DEFAULT_STATE
            under = saved.get("lighting", {}).get("under_sofa", {})
            patch = self._merge(
                patch,
                self.lighting.set_zone(
                    "under_sofa",
                    under.get("mode", "off"),
                    under.get("color", "#FFFFFF"),
                    int(under.get("brightness", 128)),
                ),
            )
            rl_on = bool(saved.get("lighting", {}).get("reading_light", {}).get("on", False))
            patch = self._merge(patch, self.reading_light.set(rl_on))
            bl_on = self._saved_back_light_on if self._saved_back_light_on is not None else bool(
                saved.get("lighting", {}).get("back_light", {}).get("on", False)
            )
            patch = self._merge(patch, self.back_light.set(bl_on))
            patch = self._merge(patch, {"mode": "normal"})
            self._saved_state = None
            self._saved_back_light_on = None
        else:
            # Activate party mode
            self.esp.send_command("NORA_box_OPEN")
            self.esp.send_command("NORA_sound_BOOST")
            self._saved_state = current
            self._saved_back_light_on = bool(
                current.get("lighting", {}).get("back_light", {}).get("on", False)
            )
            patch = self._merge(
                patch,
                self.lighting.set_zone("under_sofa", "rainbow", "#FF00FF", 255),
            )
            patch = self._merge(patch, self.reading_light.set(False))
            patch = self._merge(patch, self.back_light.set(False))
            patch = self._merge(patch, {"mode": "party"})

        return patch