import os
import subprocess
from typing import Dict, List

MOCK = os.environ.get("NORA_MOCK") == "1"


class WiFiService:
    """Service layer for controlling system Wi-Fi using nmcli."""

    def __init__(self) -> None:
        self._mock_on = True
        self._mock_ssid = ""

    # Power control -----------------------------------------------------
    def set_power(self, on: bool) -> None:
        """Enable or disable Wi-Fi radio."""
        if MOCK:
            self._mock_on = on
            if not on:
                self._mock_ssid = ""
            return
        cmd = [ "sudo", "nmcli", "radio", "wifi", "on" if on else "off"]
        try:
            subprocess.run(
                cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except Exception:
            pass

    def status(self) -> Dict[str, str]:
        """Return current Wi-Fi state and connected SSID (if any)."""
        if MOCK:
            return {"on": self._mock_on, "ssid": self._mock_ssid}
        try:
            out = (
                subprocess.check_output([ "sudo","nmcli", "radio", "wifi"], text=True)
                .strip()
                .lower()
            )
            on = out == "enabled"
            ssid = ""
            if on:
                out2 = subprocess.check_output(
                    [ "sudo","nmcli", "-t", "-f", "active,ssid", "dev", "wifi"], text=True
                )
                for line in out2.splitlines():
                    active, name = line.split(":", 1)
                    if active == "yes":
                        ssid = name
                        break
            return {"on": on, "ssid": ssid}
        except Exception:
            return {"on": False, "ssid": ""}

    # Network scanning --------------------------------------------------
    def scan(self) -> List[Dict[str, str]]:
        """Scan available networks and return list of dicts."""
        if MOCK:
            return [{"ssid": "MockAP", "signal": "70"}]
        try:
            out = subprocess.check_output(
                [ "sudo","nmcli", "-t", "-f", "ssid,signal", "dev", "wifi"], text=True
            )
            nets: List[Dict[str, str]] = []
            for line in out.splitlines():
                parts = line.split(":", 1)
                if len(parts) != 2:
                    continue
                ssid, signal = parts
                if ssid:
                    nets.append({"ssid": ssid, "signal": signal})
            return nets
        except Exception:
            return []

    # Connection management ---------------------------------------------
    def connect(self, ssid: str, password: str) -> bool:
        """Attempt to connect to a network; return True if successful."""
        if MOCK:
            if password:
                self._mock_ssid = ssid
                return True
            return False
        try:
            subprocess.check_call(
                [ "sudo","nmcli", "device", "wifi", "connect", ssid, "password", password],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except subprocess.CalledProcessError:
            return False
        except Exception:
            return False

    def forget(self, ssid: str) -> None:
        """Forget a previously connected network."""
        if MOCK:
            if self._mock_ssid == ssid:
                self._mock_ssid = ""
            return
        try:
            subprocess.run(
                [ "sudo","nmcli", "connection", "delete", ssid],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            
        except Exception:
            pass