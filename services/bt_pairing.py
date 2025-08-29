# nora/services/bt_pairing.py
import subprocess

def start_pairing_window(seconds: int = 120):
    subprocess.run(["systemctl","start","nora-bt-pair.service"], check=False)