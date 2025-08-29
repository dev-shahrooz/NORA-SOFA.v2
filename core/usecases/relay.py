from typing import Dict, Optional

class SingleRelayUsecase:
    def __init__(self, gpio_driver, name: str, pin: int, active_low: bool = False, retries: int = 2):
        self.gpio = gpio_driver
        self.name = name
        self.pin = pin
        self.active_low = active_low
        self.retries = retries
        try:
            self.gpio.setup_output(self.pin)
        except Exception:
            pass

    def _write_level(self, on: bool):
        level = 1 if on else 0
        if self.active_low:
            level = 0 if on else 1
        err: Optional[Exception] = None
        for _ in range(self.retries + 1):
            try:
                self.gpio.write(self.pin, level)
                return
            except Exception as e:
                err = e
        raise RuntimeError(f"GPIO write failed on pin {self.pin}: {err}")

    def set(self, on: bool) -> Dict:
        self._write_level(on)
        return {"lighting": {self.name: {"on": bool(on)}}}

    def toggle(self, current_on: bool) -> Dict:
        return self.set(not bool(current_on))
