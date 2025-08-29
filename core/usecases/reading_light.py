# nora/core/usecases/reading_light.py
from __future__ import annotations
from typing import Dict, Optional

class ReadingLightUsecase:
    """
    کنترل چراغ مطالعه متصل به رله روی GPIO17.
    - set(on): خاموش/روشن idempotent
    - toggle(current_on): برعکس کردن وضعیت فعلی
    """
    def __init__(self, gpio_driver, pin: int = 17, active_low: bool = False, retries: int = 2):
        self.gpio = gpio_driver
        self.pin = pin
        self.active_low = active_low
        self.retries = retries
        # اطمینان از آماده‌سازی پین به‌صورت خروجی
        try:
            self.gpio.setup_output(self.pin)
        except Exception:
            # برخی درایورها idempotent هستند؛ نادیده بگیر
            pass

    def _write_level(self, on: bool):
        # نگاشت سطح منطقی با توجه به رله Active-Low/High
        level = 0 if (self.active_low and on) else (1 if on else 0)
        # اگر active_low و off → 1، اگر active_low و on → 0، در غیر این صورت on→1/off→0
        if self.active_low and not on:
            level = 1
        attempts = 0
        last_err: Optional[Exception] = None
        while attempts <= self.retries:
            try:
                self.gpio.write(self.pin, level)
                return
            except Exception as e:
                last_err = e
                attempts += 1
        # اگر بعد از retry موفق نشد:
        raise RuntimeError(f"GPIO write failed on pin {self.pin}: {last_err}")

    def set(self, on: bool) -> Dict:
        """روشن/خاموش کردن (idempotent) و برگرداندن patch برای State."""
        self._write_level(on)
        return {"lighting": {"reading_light": {"on": bool(on)}}}

    def toggle(self, current_on: bool) -> Dict:
        """تغییر وضعیت فعلی (non-idempotent) و برگرداندن patch برای State."""
        return self.set(not bool(current_on))
