# nora/core/usecases/mode.py
from typing import Dict, Any

from core.state_store import DEFAULT_STATE


class ModeUsecase:
    """Toggle between normal and party modes.

    When entering party mode, current state is saved and various usecases are
    adjusted (lighting, reading light, audio, ...). When toggling back, saved
    values are restored.
    """

    def __init__(self, state_store, lighting_uc, audio_uc, reading_light_uc, back_light_uc):
        self.state_store = state_store
        self.lighting = lighting_uc
        self.audio = audio_uc
        self.reading_light = reading_light_uc
        self.back_light = back_light_uc
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
            vol = int(saved.get("audio", {}).get("volume", 70))
            patch = self._merge(patch, self.audio.set_volume(vol))
            patch = self._merge(patch, {"mode": "normal"})
            self._saved_state = None
            self._saved_back_light_on = None
        else:
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
            patch = self._merge(patch, self.audio.set_volume(90))
            patch = self._merge(patch, {"mode": "party"})

        return patch