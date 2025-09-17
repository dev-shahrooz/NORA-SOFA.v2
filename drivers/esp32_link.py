"""Serial link helper for communicating with the ESP32 controller."""

import os
import threading
import time

MOCK = os.environ.get("NORA_MOCK") == "1"


class ESP32Link:
    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        baud: int = 115200,
        timeout: float = 0.2,
        command_delay: float = 0.005,
    ):
        self.mock = MOCK
        self._command_delay = max(command_delay, 0.0)
        self._lock = threading.Lock()
        if not self.mock:
            import serial  # type: ignore

            self.ser = serial.Serial(port, baudrate=baud, timeout=timeout)

    def send_command(self, cmd: str) -> bool:
        """Send a raw command string to the ESP32 over serial.

        Commands are sent sequentially with a small delay between each one so the
        ESP32 has time to process them.
        """

        with self._lock:
            # Ensure commands are separated by a newline before transmission.
            if not cmd.endswith("\n"):
                cmd += "\n"

            if self.mock:
                print("[ESP32 MOCK] ->", cmd.strip())
            else:
                self.ser.write(cmd.encode())

            if self._command_delay:
                # Sleep after sending so the next command is naturally delayed.
                time.sleep(self._command_delay)

        return True