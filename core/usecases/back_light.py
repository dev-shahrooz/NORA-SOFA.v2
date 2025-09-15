# nora/core/usecases/back_light.py
from typing import Dict

class BackLightUsecase:
    """Control the back light via ESP32 commands."""
    def __init__(self, esp_link):
        self.esp = esp_link

    def set(self, on: bool) -> Dict:
        cmd = "NORA_backL_ON" if on else "NORA_backL_OFF"
        self.esp.send_command(cmd)
        return {"lighting": {"back_light": {"on": bool(on)}}}

    def toggle(self, current_on: bool) -> Dict:
        """تغییر وضعیت فعلی (non-idempotent) و برگرداندن patch برای State."""
        return self.set(not bool(current_on))
