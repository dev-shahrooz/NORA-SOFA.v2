# nora/core/usecases/lighting.py
import re
from typing import Any, Dict

class LightingService:
    """Control under-sofa and box lights via ESP32 commands."""
    
    _BRIGHTNESS_VALUES = {"low", "mid", "high"}

    def __init__(self, esp_link):
        self.esp = esp_link
    
    def _normalize_zone(self, zone: str) -> str:
        return "box" if zone == "box" else "under_sofa"

    def _normalize_mode(self, mode: Any) -> str:
        if not isinstance(mode, str):
            return "off"
        value = mode.strip().lower()
        if value in {"off", "rainbow", "static", "wakeup"}:
            return value
        if value in {"eq", "equalizer", "equalize", "equaalize"}:
            return "equaalize"
        return "off"

    def _normalize_color(self, color: Any) -> str:
        if not isinstance(color, str):
            return "#ffffff"
        candidate = color.strip().lower()
        if re.fullmatch(r"#[0-9a-f]{6}", candidate):
            return candidate
        cleaned = re.sub(r"[^0-9a-f]", "", candidate)[:6]
        return f"#{cleaned}" if len(cleaned) == 6 else "#ffffff"

    def _normalize_brightness(self, brightness: Any) -> str:
        if isinstance(brightness, str):
            value = brightness.strip().lower()
            if value in self._BRIGHTNESS_VALUES:
                return value
            if value in {"medium", "med"}:
                return "mid"
        try:
            numeric = float(brightness)
        except (TypeError, ValueError):
            return "mid"
        if numeric <= 85:
            return "low"
        if numeric <= 170:
            return "mid"
        return "high"

    def _brightness_cmd(self, brightness: str) -> str:
        if brightness not in self._BRIGHTNESS_VALUES:
            brightness = "mid"
        return f"BRIGHTNESS_{brightness}"

    def set_zone(self, zone: str, mode: Any, color: Any, brightness: Any) -> Dict:
        zone_key = self._normalize_zone(zone)
        prefix = "NORA_magicbl_" if zone_key == "box" else "NORA_magicl_"
        mode_value = self._normalize_mode(mode)
        color_value = self._normalize_color(color)
        brightness_value = self._normalize_brightness(brightness)

        if mode_value == "static":
            commands = [f"{prefix}MODE_static_{color_value}"]
        else:
          commands = [f"{prefix}MODE_{mode_value}"]
        commands.append(f"{prefix}{self._brightness_cmd(brightness_value)}")

        self.esp.send_command(commands)
        print(commands)
        return {
            "lighting": {
                zone_key: {
                    "mode": mode_value,
                    "color": color_value,
                    "brightness": brightness_value,
                }
            }
        }