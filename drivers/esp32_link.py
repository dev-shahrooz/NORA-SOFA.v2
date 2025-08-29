# nora/drivers/esp32_link.py
import json, time, serial
import os


MOCK = os.environ.get("NORA_MOCK") == "1"


class ESP32Link:
    def __init__(self, port: str="/dev/ttyUSB0", baud: int=115200, timeout: float=0.2):
        self.mock = MOCK
        if not self.mock:
            import serial
            self.ser = serial.Serial(port, baudrate=baud, timeout=timeout)

    def send_command(self, cmd: dict) -> bool:
        if self.mock:
            print("[ESP32 MOCK] ->", cmd)
            return True
        pkt = (json.dumps(cmd) + "\n").encode()
        self.ser.write(pkt)
        return True