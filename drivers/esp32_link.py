"""Serial link helper for communicating with the ESP32 controller."""

import os

MOCK = os.environ.get("NORA_MOCK") == "1"


class ESP32Link:
    def __init__(self, port: str = "/dev/ttyUSB0", baud: int = 115200, timeout: float = 0.2):
        self.mock = MOCK
        if not self.mock:
            import serial  # type: ignore
            self.ser = serial.Serial(port, baudrate=baud, timeout=timeout)

    def send_command(self, cmd: str) -> bool:
        """Send a raw command string to the ESP32 over serial."""
        if self.mock:
            print("[ESP32 MOCK] ->", cmd)
            return True
        if not cmd.endswith("\n"):
            cmd += "\n"
        self.ser.write(cmd.encode())
        return True