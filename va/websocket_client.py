# -*- coding: utf-8 -*-
# voice_assistant/websocket_client.py
# کلاینت هماهنگ با سرور Flask-SocketIO شما (nora/app.py)

import socketio
import time
import os
import sys
import threading
from typing import Optional

# اطمینان از ایمپورت پوشه فعلی
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)

# ---------- تنظیمات ----------
SERVER_URL = os.getenv("WS_SERVER_URL", "http://127.0.0.1:8080")
NAMESPACE = "/"

_sio: Optional[socketio.Client] = None
_sio_lock = threading.Lock()


def _get_client() -> socketio.Client:
    '''ایجاد singleton از socketio.Client با اتصال مطمئن به سرور'''
    global _sio
    with _sio_lock:
        if _sio is None:
            _sio = socketio.Client(
                logger=False, engineio_logger=False, reconnection=True
            )

            @_sio.event
            def connect():
                print(f"[SOCKET] ✅ Connected to {SERVER_URL}")

            @_sio.event
            def disconnect():
                print("[SOCKET] ❌ Disconnected")

        if not _sio.connected:
            try:
                _sio.connect(SERVER_URL, transports=["websocket"])
            except Exception as e:
                print("[SOCKET] Connect failed:", e)
        return _sio


# ---------- ارسال ایونت ----------
def _emit(event: str, data: dict):
    sio = _get_client()
    if sio and sio.connected:
        try:
            sio.emit(event, data)
        except Exception as e:
            print(f"[SOCKET] emit('{event}') failed:", e)
    else:
        print("[WS-Fallback] Not connected ->", event, data)


# ---------- API برای voice assistant ----------

def send_reading_light(state: bool):
    '''روشن/خاموش کردن چراغ مطالعه'''
    _emit("va.intent", {
        "type": "reading_light.set",
        "payload": {"on": bool(state)},
        "corr_id": str(int(time.time() * 1000))
    })


def send_backlight(state: bool):
    '''روشن/خاموش کردن نور پشت'''
    _emit("va.intent", {
        "type": "back_light.set",
        "payload": {"on": bool(state)},
        "corr_id": str(int(time.time() * 1000))
    })


def send_party_mode():
    '''حالت Party Mode'''
    _emit("va.intent", {
        "type": "mode.set",
        "payload": {"mode": "party"},
        "corr_id": str(int(time.time() * 1000))
    })


def send_normal_mode():
    '''بازگشت به حالت Normal Mode'''
    _emit("va.intent", {
        "type": "mode.set",
        "payload": {"mode": "normal"},
        "corr_id": str(int(time.time() * 1000))
    })


# def send_equalizer1():
#     _emit("va.intent", {
#         "type": "audio.equalizer",
#         "payload": {"preset": 1},
#         "corr_id": str(int(time.time() * 1000))
#     })


# def send_equalizer2():
#     _emit("va.intent", {
#         "type": "audio.equalizer",
#         "payload": {"preset": 2},
#         "corr_id": str(int(time.time() * 1000))
#     })


# def send_equalizer3():
#     _emit("va.intent", {
#         "type": "audio.equalizer",
#         "payload": {"preset": 3},
#         "corr_id": str(int(time.time() * 1000))
#     })


# def send_equalizer_off():
#     _emit("va.intent", {
#         "type": "audio.equalizer",
#         "payload": {"preset": "off"},
#         "corr_id": str(int(time.time() * 1000))
#     })
