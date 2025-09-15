# nora/core/usecases/reading_light.py
from __future__ import annotations
from typing import Dict, Optional

class ReadingLightUsecase:
    """Control the reading light via ESP32 commands."""
    def __init__(self, esp_link):
        self.esp = esp_link


    def set(self, on: bool) -> Dict:
        cmd = "NORA_readingL_ON" if on else "NORA_readingL_OFF"
        self.esp.send_command(cmd)
        return {"lighting": {"reading_light": {"on": bool(on)}}}

    def toggle(self, current_on: bool) -> Dict:
        return self.set(not bool(current_on))
