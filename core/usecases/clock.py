"""Clock configuration use case for sending time updates to the ESP32."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class _TimeComponents:
    hour: int
    minute: int
    second: int

    def as_string(self) -> str:
        return f"{self.hour:02d}:{self.minute:02d}:{self.second:02d}"


class ClockUsecase:
    """Handle clock related commands for the smart sofa controller."""

    def __init__(self, esp_link):
        self.esp = esp_link

    @staticmethod
    def _coerce_component(value: Optional[object], max_value: int) -> Optional[int]:
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return None
        try:
            ivalue = int(value)
        except (TypeError, ValueError):
            return None
        if not 0 <= ivalue <= max_value:
            return None
        return ivalue

    @classmethod
    def _parse_time(
        cls,
        hour: Optional[object] = None,
        minute: Optional[object] = None,
        second: Optional[object] = None,
        time_str: Optional[str] = None,
    ) -> Optional[_TimeComponents]:
        if time_str and not any(v is not None for v in (hour, minute, second)):
            parts = time_str.split(":")
            if len(parts) == 3:
                hour, minute, second = parts
            elif len(parts) == 2:
                hour, minute = parts
                second = "0"
        h = cls._coerce_component(hour, 23)
        m = cls._coerce_component(minute, 59)
        s = cls._coerce_component(second, 59)
        if h is None or m is None:
            return None
        if s is None:
            s = 0
        return _TimeComponents(h, m, s)

    def _send_command(self, time_value: _TimeComponents) -> None:
        if self.esp is None:
            return
        cmd = f"NORA_clock_TIME_{time_value.as_string()}"
        self.esp.send_command(cmd)

    def set_time(
        self,
        hour: Optional[object] = None,
        minute: Optional[object] = None,
        second: Optional[object] = None,
        time_str: Optional[str] = None,
    ) -> Dict[str, Dict[str, str]]:
        time_value = self._parse_time(hour, minute, second, time_str)
        if time_value is None:
            raise ValueError("Invalid time components")
        self._send_command(time_value)
        return {"clock": {"time": time_value.as_string()}}

    def apply_time_string(self, time_str: str) -> None:
        time_value = self._parse_time(time_str=time_str)
        if time_value is None:
            return
        self._send_command(time_value)