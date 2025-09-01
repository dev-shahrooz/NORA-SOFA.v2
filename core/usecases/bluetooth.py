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