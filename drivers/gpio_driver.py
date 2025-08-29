# nora/drivers/gpio_driver.py
class GPIO:
    @staticmethod
    def set(pin: int, value: bool):
        print(f"[GPIO] set {pin} -> {value}")



# nora/drivers/gpio_driver.py
"""
GPIO driver for Nora v2 using lgpio on Raspberry Pi with a Mock fallback.

Usage:
    from nora.drivers.gpio_driver import GPIODriver
    gpio = GPIODriver(chip=0)  # /dev/gpiochip0
    gpio.setup_output(17, initial=0)
    gpio.write(17, 1)

Behavior:
- If env NORA_MOCK=1 or lgpio import fails, uses a harmless Mock that just logs calls.
- On real Pi, uses lgpio with an opened gpiochip handle.
"""
import os
from typing import Optional

__all__ = ["GPIODriver"]

MOCK = os.environ.get("NORA_MOCK") == "1"

class _MockGPIO:
    def __init__(self):
        self._vals = {}
        print("[GPIO MOCK] initialized")

    def setup_output(self, pin: int, initial: int = 0):
        self._vals[pin] = initial
        print(f"[GPIO MOCK] setup_output pin={pin} initial={initial}")

    def write(self, pin: int, level: int):
        self._vals[pin] = int(level)
        print(f"[GPIO MOCK] write pin={pin} level={level}")

    def close(self):
        print("[GPIO MOCK] close()")

try:
    if not MOCK:
        import lgpio  # type: ignore
    else:
        lgpio = None  # noqa: F401
except Exception:
    # Fallback to mock if lgpio unavailable (e.g., on Windows/WSL)
    lgpio = None  # type: ignore

class GPIODriver:
    def __init__(self, chip: int = 0):
        """Open gpiochip and prepare driver.
        On mock mode, no real chip is opened.
        """
        self._mock = MOCK or (lgpio is None)
        self._chip = chip
        self._h: Optional[int] = None
        if self._mock:
            self._impl = _MockGPIO()
        else:
            # Open gpiochipN
            self._h = lgpio.gpiochip_open(self._chip)
            self._impl = None

    # ---- Public API ----
    def setup_output(self, pin: int, initial: int = 0):
        """Claim pin as output and set initial level (0/1)."""
        if self._mock:
            self._impl.setup_output(pin, initial)
            return
        assert self._h is not None
        # Set output drive with initial value
        lgpio.gpio_claim_output(self._h, pin, initial)

    def write(self, pin: int, level: int):
        """Write logical level 0/1 to pin."""
        if self._mock:
            self._impl.write(pin, int(level))
            return
        assert self._h is not None
        lgpio.gpio_write(self._h, pin, int(level))

    def close(self):
        if self._mock:
            self._impl.close()
            return
        if self._h is not None:
            try:
                lgpio.gpiochip_close(self._h)
            finally:
                self._h = None

    # Context manager support
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
