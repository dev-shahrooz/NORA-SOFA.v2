"""Serial link helper for communicating with the ESP32 controller."""

import os
import threading
import time
import serial

MOCK = os.environ.get("NORA_MOCK") == "1"

class ESP32Link:
    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        baud: int = 115200,
        timeout: float = 0.5,  # افزایش تایم‌اوت
        command_delay: float = 0.005,
    ):
        self.mock = MOCK
        self._command_delay = max(command_delay, 0.0)
        self._lock = threading.Lock()
        if not self.mock:
            import serial
            self.ser = serial.Serial(port, baudrate=baud, timeout=timeout)
            self.start_reader_thread()  # شروع نخ خواندن

    def start_reader_thread(self) -> None:
        """Start a background thread to continuously read serial data."""
        if self.mock:
            return

        def reader():
            while True:
                try:
                    if self.ser.in_waiting > 0:
                        data = self.ser.read(self.ser.in_waiting)
                        print(f"[ESP32] Received: {data.decode('utf-8', errors='ignore')}")
                    time.sleep(0.1)
                except serial.SerialException as e:
                    print(f"[ESP32] Reader error: {e}")
                    time.sleep(1)

        reader_thread = threading.Thread(target=reader, daemon=True)
        reader_thread.start()

    def clear_buffer(self) -> None:
        """Read and discard data from the serial buffer to prevent overflow."""
        if self.mock:
            return
        try:
            if self.ser.in_waiting > 0:
                data = self.ser.read(self.ser.in_waiting)
                print(f"[ESP32] Cleared buffer: {data.decode('utf-8', errors='ignore')}")
        except serial.SerialException as e:
            print(f"[ESP32] Buffer clear error: {e}")

    def reconnect(self) -> bool:
        """Attempt to reconnect to the serial port."""
        if self.mock:
            return True
        try:
            self.ser.close()
            self.ser.open()
            print(f"[ESP32] Reconnected to {self.ser.port}")
            return True
        except serial.SerialException as e:
            print(f"[ESP32] Reconnect error: {e}")
            return False

    def send_command(self, cmd: str) -> bool:
        """Send a raw command string to the ESP32 over serial."""
        with self._lock:
            if not cmd.endswith("\n"):
                cmd += "\n"

            if self.mock:
                print("[ESP32 MOCK] ->", cmd.strip())
            else:
                try:
                    self.clear_buffer()
                    self.ser.write(cmd.encode())
                except serial.SerialException as e:
                    print(f"[ESP32] Send error: {e}")
                    if e.errno == 5:
                        print("[ESP32] I/O error detected, attempting reconnect")
                        self.reconnect()
                    return False

            if self._command_delay:
                time.sleep(self._command_delay)

        return True