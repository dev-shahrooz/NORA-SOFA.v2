# nora/core/usecases/mode.py
from typing import Dict, Any
import time

from core.state_store import DEFAULT_STATE


class ModeUsecase:
    """Toggle between normal and party modes.

    When entering party mode, current state is saved and various usecases are
    adjusted (lighting, reading light, ...). When toggling back, saved
    values are restored.
    """

    def __init__(
        self,
        state_store,
        lighting_uc,
        reading_light_uc,
        back_light_uc,
        gpio_driver,
        open_box_uc,
        close_box_uc,
        party_mode_amp_uc,
    ):
        self.state_store = state_store
        self.lighting = lighting_uc
        self.reading_light = reading_light_uc
        self.back_light = back_light_uc
        self.open_pin = open_box_uc
        self.close_pin = close_box_uc
        self.party_pin = party_mode_amp_uc
        self.gpio = gpio_driver
        self._saved_state: Dict[str, Any] | None = None
        self._saved_back_light_on: bool | None = None
         # Prepare GPIO pins for party mode indicators
        for pin in (open_box_uc, party_mode_amp_uc, close_box_uc):
            try:
                self.gpio.setup_output(pin, 0)
            except Exception:
                pass

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
            # Deactivate party mode GPIO sequence
            try:
                self.gpio.write(self.party_pin, 0)
                self.gpio.write(self.close_pin, 1)
                time.sleep(8)
                self.gpio.write(self.close_pin, 0)
            except Exception:
                pass

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
            # Activate party mode GPIO sequence
            try:
                self.gpio.write(self.open_pin, 1)
                time.sleep(8)
                self.gpio.write(self.open_pin, 0)
                self.gpio.write(self.party_pin, 1)
            except Exception:
                pass
            
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