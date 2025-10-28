# -*- coding: utf-8 -*-
# voice_assistant/command_parser.py
# فقط عبارات دقیق پذیرفته می‌شوند و از websocket_client (همین پوشه) استفاده می‌کنیم.


from typing import Callable, Dict
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)  # تا ایمپورت مطلقِ فایل‌های کنار همین فایل کار کند


# --- تلاش برای ایمپورت مطلق از فایل کنار همین ماژول
try:
    from websocket_client import (
        send_reading_light,
        send_backlight,
        send_party_mode,
        send_normal_mode,
    )
except Exception as e:
    # فالبک امن برای توسعه: برنامه نترکه اما روی سوکت واقعی هم چیزی نمی‌رود
    print("[WS-Fallback] websocket_client import failed:", e)
    def _log(*a, **k): print("[WS-Fallback]", *a)
    def send_reading_light(state: bool): _log("send_reading_light", state)
    def send_backlight(state: bool): _log("send_backlight", state)
    def send_box(state: bool): _log("send_box", state)
    def send_equalizer_off(): _log("send_equalizer_off")


def _norm(t: str) -> str:
    t = (t or "").lower().strip()
    return " ".join(t.split())


# فقط همین عبارات دقیق
COMMANDS: Dict[str, Callable[[], None]] = {
    # Reading light
    "turn on the reading light": lambda: send_reading_light(True),
    "turn off the reading light": lambda: send_reading_light(False),

    # Back light
    "turn on the back light": lambda: send_backlight(True),
    "turn off the back light": lambda: send_backlight(False),

    # Box relays
    "party mode": lambda: send_party_mode(),
    "normal mode": lambda: send_normal_mode(),

    # Equalizer modes
    # "equalizer one":              send_equalizer1,
    # "equalizer two":              send_equalizer2,
    # "equalizer three":            send_equalizer3,
    # "equalizer off":              send_equalizer_off,
}


def handle_command(text: str) -> bool:
    t = _norm(text)
    action = COMMANDS.get(t)
    if not action:
        return False
    try:
        action()
        return True
    except Exception as e:
        print(f"[command_parser] Error executing '{t}': {e}")
        return False
