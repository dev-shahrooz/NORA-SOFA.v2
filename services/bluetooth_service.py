import os
import subprocess

MOCK = os.environ.get("NORA_MOCK") == "1"

class BluetoothService:
    def __init__(self):
        self._mock_on = True

    def set_power(self, on: bool):
        """Power on/off Bluetooth using bluetoothctl."""
        if MOCK:
            self._mock_on = on
            return
        cmd = ["bluetoothctl", "power", "on" if on else "off"]
        try:
            subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def status(self) -> bool:
        """Return current Bluetooth power status."""
        if MOCK:
            return self._mock_on
        try:
            out = subprocess.check_output(["bluetoothctl", "show"], text=True)
            for line in out.splitlines():
                if "Powered:" in line:
                    return line.strip().split()[-1].lower() == "yes"
        except Exception:
            pass
        return False