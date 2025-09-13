from typing import Dict
from services.wifi_service import WiFiService


class WiFiUsecase:
    """Usecase layer for Wi-Fi interactions."""

    def __init__(self, svc: WiFiService):
        self.svc = svc

    def set(self, on: bool) -> Dict:
        self.svc.set_power(on)
        st = self.svc.status()
        return {"wifi": {"on": st.get("on", False), "ssid": st.get("ssid", "")}}

    def toggle(self, current_on: bool) -> Dict:
        return self.set(not bool(current_on))

    def scan(self) -> Dict:
        nets = self.svc.scan()
        return {"wifi": {"networks": nets}}

    def connect(self, ssid: str, password: str) -> Dict:
        ok = self.svc.connect(ssid, password)
        return {"wifi": {"connected": ok, "ssid": ssid if ok else ""}}

    def forget(self, ssid: str) -> Dict:
        self.svc.forget(ssid)
        # After forgetting a network we are no longer connected to it
        return {"wifi": {"forgot": ssid, "connected": False, "ssid": ""}}