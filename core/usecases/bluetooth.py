from typing import Dict
from services.bluetooth_service import BluetoothService

class BluetoothUsecase:
    def __init__(self, bt_service: BluetoothService):
        self.bt = bt_service
    
    def _status_patch(self) -> Dict:
        on = bool(self.bt.status())
        connected_info = {"connected": False, "name": "", "address": ""}
        if on:
            connected_info = self.bt.connected_device()

        connected = bool(connected_info.get("connected"))
        address = connected_info.get("address", "") or ""
        name = connected_info.get("name", "") or address

        if not on:
            connected = False
            name = ""
            address = ""

        return {
            "bluetooth": {
                "on": on,
                "connected": connected,
                "device_name": name,
                "device_address": address,
            }
        }

    def set(self, on: bool) -> Dict:
        self.bt.set_power(on)
        return self._status_patch()


    def toggle(self, current_on: bool) -> Dict:
        return self.set(not bool(current_on))

    def unpair(self) -> Dict:
        """Trigger Bluetooth unpair through the service layer."""
        self.bt.unpair()
        patch = self._status_patch()
        patch.setdefault("bluetooth", {})["unpaired"] = True
        return patch