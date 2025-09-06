# nora/services/bt_pairing.py
"""Helpers for starting Bluetooth pairing."""
import subprocess

SCRIPT_PATH = "/usr/local/bin/nora-bt-pair.sh"


def start_pairing_window(seconds: int = 120) -> None:
    """Open a Bluetooth pairing window for the given number of seconds.

    If ``seconds`` matches the default service configuration (120) the
    systemd unit is used. Otherwise the helper script is invoked directly
    with the requested timeout.
    """
    if seconds == 120:
        subprocess.run(["systemctl", "start", "nora-bt-pair.service"], check=False)
    else:
        subprocess.run([SCRIPT_PATH, str(int(seconds))], check=False)