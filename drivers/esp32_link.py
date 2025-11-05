# """Serial link helper for communicating with the ESP32 controller."""

# import os
# import threading
# import time
# import serial

# MOCK = os.environ.get("NORA_MOCK") == "1"

# class ESP32Link:
#     def __init__(
#         self,
#         port: str = "/dev/ttyUSB0",
#         baud: int = 115200,
#         timeout: float = 0.5,  # افزایش تایم‌اوت
#         command_delay: float = 0.005,
#     ):
#         self.mock = MOCK
#         self._command_delay = max(command_delay, 0.0)
#         self._lock = threading.Lock()
#         if not self.mock:
#             import serial
#             self.ser = serial.Serial(port, baudrate=baud, timeout=timeout)
#             self.start_reader_thread()  # شروع نخ خواندن

#     def start_reader_thread(self) -> None:
#         """Start a background thread to continuously read serial data."""
#         if self.mock:
#             return

#         def reader():
#             while True:
#                 try:
#                     if self.ser.in_waiting > 0:
#                         data = self.ser.read(self.ser.in_waiting)
#                         print(f"[ESP32] Received: {data.decode('utf-8', errors='ignore')}")
#                     time.sleep(0.1)
#                 except serial.SerialException as e:
#                     print(f"[ESP32] Reader error: {e}")
#                     time.sleep(1)

#         reader_thread = threading.Thread(target=reader, daemon=True)
#         reader_thread.start()

#     def clear_buffer(self) -> None:
#         """Read and discard data from the serial buffer to prevent overflow."""
#         if self.mock:
#             return
#         try:
#             if self.ser.in_waiting > 0:
#                 data = self.ser.read(self.ser.in_waiting)
#                 print(f"[ESP32] Cleared buffer: {data.decode('utf-8', errors='ignore')}")
#         except serial.SerialException as e:
#             print(f"[ESP32] Buffer clear error: {e}")

#     def reconnect(self) -> bool:
#         """Attempt to reconnect to the serial port."""
#         if self.mock:
#             return True
#         try:
#             self.ser.close()
#             self.ser.open()
#             print(f"[ESP32] Reconnected to {self.ser.port}")
#             return True
#         except serial.SerialException as e:
#             print(f"[ESP32] Reconnect error: {e}")
#             return False

#     def send_command(self, cmd: str) -> bool:
#         """Send a raw command string to the ESP32 over serial."""
#         with self._lock:
#             if not cmd.endswith("\n"):
#                 cmd += "\n"

#             if self.mock:
#                 print("[ESP32 MOCK] ->", cmd.strip())
#             else:
#                 try:
#                     self.clear_buffer()
#                     self.ser.write(cmd.encode())
#                 except serial.SerialException as e:
#                     print(f"[ESP32] Send error: {e}")
#                     if e.errno == 5:
#                         print("[ESP32] I/O error detected, attempting reconnect")
#                         self.reconnect()
#                     return False

#             if self._command_delay:
#                 time.sleep(self._command_delay)

#         return True


# esp32_link.py
from __future__ import annotations

import os
import threading
import time
from typing import Callable, Optional, Iterable

try:
    import serial
    import serial.tools.list_ports
except Exception as e:
    serial = None  # type: ignore
    print("[ESP32] pyserial not available:", e)

# اگر می‌خواهی حالت شبیه‌ساز داشته باشی:
MOCK = os.environ.get("NORA_MOCK") == "1"

# کلیدواژه‌هایی که در توضیحات پورت کمک می‌کنند ESP32 را تشخیص دهیم
IDENT_KEYWORDS = ("ch340", "ch341", "cp210", "ft232", "esp32", "silicon labs", "espressif")


class ESP32Link:
    """
    لینک سریال با قابلیت خودترمیم:
      - اگر USB قطع/وصل شود، خودش دنبال پورت جدید می‌گردد و وصل می‌شود.
      - بعد از وصل مجدد، callback اختیاری on_reconnect را صدا می‌زند تا state دوباره اعمال شود.
      - send_command اگر خطا خورد، یک بار reconnect و retry می‌کند.
    """

    def __init__(
        self,
        port: str = "/dev/ttyACM0",
        baud: int = 115200,
        timeout: float = 0.5,
        command_delay: float = 0.005,
        on_reconnect: Optional[Callable[[], None]] = None,
        port_finder: Optional[Callable[[], str]] = None,
        start_reader: bool = True,
    ) -> None:
        self.mock = MOCK or (serial is None)
        self._command_delay = max(command_delay, 0.0)
        self._lock = threading.Lock()
        self._baud = baud
        self._timeout = timeout
        self._last_port = port
        self._on_reconnect = on_reconnect
        self._port_finder = port_finder
        self._reader_thread: Optional[threading.Thread] = None
        self._stop = False
        self.ser = None  # type: ignore

        if not self.mock:
            self._open(self._last_port)
            if start_reader:
                self.start_reader_thread()
        else:
            print("[ESP32 MOCK] initialized")

    # ----------------------
    # اتصال / قطع / باز کردن
    # ----------------------
    def _open(self, port: str) -> None:
        if self.mock:
            return
        # اگر قبلاً باز است، ببند
        try:
            if getattr(self, "ser", None) and self.ser and self.ser.is_open:
                self.ser.close()
        except Exception:
            pass

        self.ser = serial.Serial(port, baudrate=self._baud, timeout=self._timeout)
        self._last_port = port
        print(f"[ESP32] Opened {port}")

    def close(self) -> None:
        self._stop = True
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
        except Exception:
            pass

    # ----------------------
    # کشف پورت‌های کاندید
    # ----------------------
    def _iter_candidate_ports(self) -> Iterable[str]:
        # 1) مسیرهای پایدار by-id
        try:
            byid = "/dev/serial/by-id"
            if os.path.isdir(byid):
                # اول Espressif ها
                for name in sorted(os.listdir(byid)):
                    if "Espressif" in name or "espressif" in name.lower():
                        yield os.path.join(byid, name)
                # بعد بقیه
                for name in sorted(os.listdir(byid)):
                    yield os.path.join(byid, name)
        except Exception:
            pass

        # 2) comports()
        try:
            for p in serial.tools.list_ports.comports():
                desc = (p.description or "").lower()
                if any(k in desc for k in IDENT_KEYWORDS) or p.vid or p.pid:
                    yield p.device
        except Exception:
            pass

        # 3) متغیر محیطی و fallback
        env_port = os.environ.get("ESP_PORT")
        if env_port:
            yield env_port
        for fallback in ("/dev/esp32", "/dev/ttyACM0", "/dev/ttyUSB0"):
            yield fallback

    # ----------------------
    # reconnect هوشمند
    # ----------------------
    def reconnect_any(self) -> bool:
        """سعی کن روی پورت قبلی وصل شوی؛ اگر نشد، بین پورت‌های کاندید بگرد؛
        در نهایت اگر port_finder داریم، از آن کمک بگیر."""
        if self.mock:
            print("[ESP32 MOCK] reconnect_any -> OK")
            return True

        # پورت قبلی
        try:
            self._open(self._last_port)
            print(f"[ESP32] Reconnected to previous port {self._last_port}")
            return True
        except Exception as e:
            print(f"[ESP32] Previous port failed: {e}")

        # اسکن پورت‌ها
        for dev in self._iter_candidate_ports():
            try:
                self._open(dev)
                print(f"[ESP32] Reconnected to new port {dev}")
                return True
            except Exception:
                time.sleep(0.15)
                continue

        # port_finder سفارشی
        if self._port_finder:
            try:
                dev = self._port_finder()
                self._open(dev)
                print(f"[ESP32] Reconnected via port_finder to {dev}")
                return True
            except Exception as e:
                print(f"[ESP32] port_finder failed: {e}")

        return False

    # ----------------------
    # reader thread
    # ----------------------
    def start_reader_thread(self) -> None:
        if self.mock or self._reader_thread is not None:
            return

        def reader():
            while not self._stop:
                try:
                    if self.ser and self.ser.in_waiting > 0:
                        data = self.ser.read(self.ser.in_waiting)
                        if data:
                            print(f"[ESP32] << {data.decode('utf-8', errors='ignore')}")
                    time.sleep(0.1)
                except serial.SerialException as e:
                    if self._stop:
                        return
                    print(f"[ESP32] Reader error: {e} -> trying to reconnect...")
                    while not self._stop and not self.reconnect_any():
                        time.sleep(1.0)
                    if self._stop:
                        return
                    # بعد از اتصال موفق، callback را صدا بزن
                    try:
                        if self._on_reconnect:
                            self._on_reconnect()
                    except Exception as cb_err:
                        print(f"[ESP32] on_reconnect callback error: {cb_err}")
                except Exception as e:
                    # خطاهای خواندن غیر سریالی
                    print(f"[ESP32] Reader generic error: {e}")
                    time.sleep(0.2)

        self._reader_thread = threading.Thread(target=reader, daemon=True)
        self._reader_thread.start()

    # ----------------------
    # ابزارهای ارسال و پاک‌سازی بافر
    # ----------------------
    def clear_buffer(self) -> None:
        if self.mock:
            return
        try:
            if self.ser and self.ser.in_waiting > 0:
                data = self.ser.read(self.ser.in_waiting)
                if data:
                    print(f"[ESP32] Cleared buffer: {data.decode('utf-8', errors='ignore')}")
        except serial.SerialException as e:
            print(f"[ESP32] Buffer clear error: {e}")

    def send_command(self, cmd: str) -> bool:
        """یک خط دستور بفرست؛ روی خطا یک بار reconnect و retry می‌کند."""
        if not cmd.endswith("\n"):
            cmd = cmd + "\n"

        with self._lock:
            if self.mock:
                print("[ESP32 MOCK] ->", cmd.strip())
                time.sleep(self._command_delay)
                return True

            try:
                self.clear_buffer()
                if not self.ser or not self.ser.is_open:
                    raise serial.SerialException("Serial not open")
                self.ser.write(cmd.encode("utf-8"))
            except Exception as e:
                print(f"[ESP32] Send error: {e} -> reconnect and retry once")
                if not self.reconnect_any():
                    return False
                try:
                    self.clear_buffer()
                    if not self.ser or not self.ser.is_open:
                        raise serial.SerialException("Serial not open after reconnect")
                    self.ser.write(cmd.encode("utf-8"))
                except Exception as e2:
                    print(f"[ESP32] Retry failed: {e2}")
                    return False

            if self._command_delay:
                time.sleep(self._command_delay)

        return True
