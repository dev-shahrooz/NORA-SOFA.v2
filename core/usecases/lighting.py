# nora/core/usecases/lighting.py
from typing import Dict

class LightingService:
    """Control under-sofa and box lights via ESP32 commands."""
    def __init__(self, esp_link):
        self.esp = esp_link
    
    def _brightness_cmd(self, brightness: int) -> str:
        if brightness <= 0:
            return "BRIGHTNESS_off"
        if brightness <= 85:
            return "BRIGHTNESS_low"
        if brightness <= 170:
            return "BRIGHTNESS_mid"
        return "BRIGHTNESS_high"    

    def set_zone(self, zone: str, mode: str, color: str, brightness: int) -> Dict:
        prefix = "NORA_magicL_" if zone == "under_sofa" else "NORA_magicBL_"
        cmds = []
        if mode == "off":
            cmds.append(prefix + "BRIGHTNESS_off")
        else:
            if mode == "static":
                cmds.append(f"{prefix}MODE_static_{color}")
            else:
                cmds.append(f"{prefix}MODE_{mode}")
            cmds.append(prefix + self._brightness_cmd(brightness))
        for c in cmds:
            self.esp.send_command(c)
        return {"lighting": {zone: {"mode": mode, "color": color, "brightness": int(brightness)}}}