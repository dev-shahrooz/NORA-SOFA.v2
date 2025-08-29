# nora/core/usecases/lighting.py
from typing import Dict

class LightingService:
    def __init__(self, esp_link):
        self.esp = esp_link

    def set_zone(self, zone: str, mode: str, color: str, brightness: int) -> Dict:
        # zone: under_sofa | box
        # mode: off|rainbow|static|eq
        cmd = {
            "cmd": "set_light",
            "zone": zone,
            "mode": mode,
            "color": color,
            "brightness": int(brightness)
        }
        ok = self.esp.send_command(cmd)
        return {"lighting": {zone: {"mode": mode, "color": color, "brightness": int(brightness)}}}