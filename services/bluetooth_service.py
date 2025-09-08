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
            print("bluetooth_service")
            print(cmd)
            subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if on:
            # مثال: بلوتوث discoverable و pairable بشه
                subprocess.run(["bluetoothctl", "discoverable", "on"], check=False)
                subprocess.run(["bluetoothctl", "pairable", "on"], check=False)

            # اگر بخوای یه سرویس هم استارت بشه
            # subprocess.run(["systemctl", "start", "nora-bt-helper.service"], check=False)

            else:
            # وقتی خاموش میشه، برعکسش رو انجام بده
                subprocess.run(["bluetoothctl", "discoverable", "off"], check=False)
                subprocess.run(["bluetoothctl", "pairable", "off"], check=False)

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

    def unpair(self) -> None:
        """Trigger Bluetooth unpair via systemd, non-blocking."""
        if MOCK:
            return
        ucmd = ["sudo", "systemctl", "start", "--no-block", "nora-bt-pair.service"]
        subprocess.run(ucmd,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )