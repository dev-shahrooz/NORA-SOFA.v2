from typing import Dict
from services.bluetooth_service import BluetoothService

class BluetoothUsecase:
    def __init__(self, bt_service: BluetoothService):
        self.bt = bt_service

    def set(self, on: bool) -> Dict:
        self.bt.set_power(on)
        return {"bluetooth": {"on": bool(self.bt.status())}}

    def toggle(self, current_on: bool) -> Dict:
        return self.set(not bool(current_on))

    def pair(self, seconds: int = 120) -> Dict:
        """
        Start a Bluetooth pairing window through the service layer.
        Non-blocking (systemctl --no-block).
        """
        secs = max(10, min(int(seconds), 600))
        self.bt.start_pair_mode(secs)
        # چون state خاصی برای pair نگه نمی‌داری، همین ACK سبک خوبه:
        return {"bluetooth": {"pairing_started": True, "seconds": secs}}