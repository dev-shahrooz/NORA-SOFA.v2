# nora/core/usecases/mode.py
from typing import Dict, Any
import time

from core.state_store import DEFAULT_STATE


class ModeUsecase:
    """Toggle between normal and party modes using ESP32 for hardware control."""


    def __init__(self, state_store, lighting_uc, esp_link):

        self.state_store = state_store
        self.lighting = lighting_uc
        self.esp = esp_link
        self._saved_state: Dict[str, Any] | None = None
        self._motor_busy_until: float = 0.0
        self._motor_block_duration: float = 8.5
        
    def _merge(self, base: Dict, update: Dict) -> Dict:
        for k, v in update.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict):
                base[k].update(v)
            else:
                base[k] = v
        return base

    def toggle(self) -> Dict:
        now = time.monotonic()
        if now < self._motor_busy_until:
            return {}

        self._motor_busy_until = now + self._motor_block_duration

        current = self.state_store.get_state()
        patch: Dict[str, Any] = {}

        if current.get("mode") == "party":
            # Return to normal mode
            self.esp.send_command("NORA_box_CLOSE")
            time.sleep(0.05)
            self.esp.send_command("NORA_sound_ON")
            time.sleep(0.05)
            saved = self._saved_state or DEFAULT_STATE
            time.sleep(0.05)
            under = saved.get("lighting", {}).get("under_sofa", {})
            time.sleep(0.05)
            patch = self._merge(
                patch,
                self.lighting.set_zone(
                    "under_sofa",
                    under.get("mode", "off"),
                    under.get("color", "#FFFFFF"),
                    int(under.get("brightness", 128)),
                ),
            )
            # Reading/back lights intentionally remain untouched so they keep their
            # most recent state across mode switches.
            time.sleep(0.05)
            patch = self._merge(patch, {"mode": "normal"})
            time.sleep(0.05)
            self._saved_state = None
        else:
            # Activate party mode
            self.esp.send_command("NORA_box_OPEN")
            time.sleep(0.05)
            self.esp.send_command("NORA_sound_BOOST")
            time.sleep(0.05)
            self._saved_state = current
            time.sleep(0.05)
            patch = self._merge(
                patch,
                self.lighting.set_zone("under_sofa", "rainbow", "#FF00FF", 255),
            )
            # Leave reading/back lights as-is during party mode activation as well.
            time.sleep(0.05)
            patch = self._merge(patch, {"mode": "party"})

        return patch