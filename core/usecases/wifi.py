from typing import Any, Dict
from services.wifi_service import WiFiService


class WiFiUsecase:
    """Usecase layer for Wi-Fi interactions."""

    def __init__(self, svc: WiFiService):
        self.svc = svc


    def _status_patch(self) -> Dict[str, Dict[str, Any]]:
        st = self.svc.status()
        wifi_state: Dict[str, Any] = {
            "on": st.get("on", False),
            "ssid": st.get("ssid", ""),
            "connected": st.get("connected", bool(st.get("ssid"))),
            "saved_networks": st.get("saved_networks", []),
        }
        return {"wifi": wifi_state}

    def set(self, on: bool) -> Dict[str, Dict[str, Any]]:
        self.svc.set_power(on)
        return self._status_patch()
    
    def toggle(self, current_on: bool) -> Dict[str, Dict[str, Any]]:
        return self.set(not bool(current_on))

    def scan(self) -> Dict[str, Dict[str, Any]]:
        nets = self.svc.scan()
        patch = self._status_patch()
        patch["wifi"]["networks"] = nets
        return patch

    def connect(self, ssid: str, password: str) -> Dict[str, Dict[str, Any]]:
        ok = self.svc.connect(ssid, password)
        patch = self._status_patch()
        patch["wifi"]["last_connection_attempt"] = {"ssid": ssid, "success": ok}
        return patch

    def forget(self, ssid: str) -> Dict[str, Dict[str, Any]]:
        self.svc.forget(ssid)
        patch = self._status_patch()
        patch["wifi"]["forgot"] = ssid
        return patch