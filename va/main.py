# import os
# import sys
# import json
# import time
# import signal
# import threading
# import traceback
# from vosk import Model, KaldiRecognizer
# import sounddevice as sd
# import socketio
# from websocket_client import (
#     _emit,
#     add_control_listener,
#     add_state_listener,
#     request_state,
# )

# HERE = os.path.dirname(os.path.abspath(__file__))
# if HERE not in sys.path:
#     sys.path.append(HERE)

# # تنظیمات
# MODEL_PATH = os.path.join(HERE, "model")
# RATE = 16000
# BLOCKSIZE = 4000
# CHANNELS = 1
# WAKE_WORD = "nora"
# COMMAND_TIMEOUT_SEC = 5
# FINAL_SILENCE_MS = 1200

# wake_word_enabled = True
# _wake_lock = threading.Lock()
# _manual_listen_event = threading.Event()


# def _set_wake_word_enabled(enabled: bool) -> bool:
#     global wake_word_enabled
#     enabled = bool(enabled)
#     with _wake_lock:
#         if wake_word_enabled != enabled:
#             wake_word_enabled = enabled
#             status = "ENABLED" if enabled else "DISABLED"
#             print(f"[VA] Wake word {status} via remote control")
#         return wake_word_enabled


# def _on_state_update(state: dict):
#     try:
#         va_cfg = (state or {}).get("voice_assistant", {})
#         _set_wake_word_enabled(va_cfg.get("wake_word_enabled", True))
#     except Exception as exc:
#         print("[VA] Failed to parse state update:", exc)


# def _on_control_event(message: dict):
#     msg_type = (message or {}).get("type")
#     if msg_type == "listen_once":
#         print("[VA] Manual listen requested from UI")
#         _manual_listen_event.set()
#     elif msg_type == "wake_word" and "enabled" in message:
#         _set_wake_word_enabled(message.get("enabled", True))


# # ایمپورت پارسر
# try:
#     from command_parser import handle_command, COMMANDS
# except Exception as e:
#     print("[FATAL] Cannot import command_parser:", e)
#     sys.exit(1)


# def _as_bytes(chunk):
#     """Ensure bytes for Vosk (fix cffi buffer issue)."""
#     # اگر قبلاً bytes/bytearray هست، همونو بده؛ وگرنه تبدیل کن
#     if isinstance(chunk, (bytes, bytearray)):
#         return chunk
#     try:
#         # خیلی از آبجکت‌های بافرپذیر با memoryview.tobytes درست می‌شن
#         return memoryview(chunk).tobytes()
#     except Exception:
#         return bytes(chunk)


# def build_wake_recognizer(model: Model) -> KaldiRecognizer:
#     grammar = json.dumps([WAKE_WORD])
#     rec = KaldiRecognizer(model, RATE, grammar)
#     try:
#         rec.SetWords(True)
#         rec.SetMaxAlternatives(0)
#     except Exception:
#         pass
#     print("[ASR] Wake grammar active:", grammar)
#     return rec


# def build_command_recognizer(model: Model) -> KaldiRecognizer:
#     phrases = list(COMMANDS.keys())
#     grammar = json.dumps(phrases)
#     rec = KaldiRecognizer(model, RATE, grammar)
#     try:
#         rec.SetWords(True)
#         rec.SetMaxAlternatives(0)
#     except Exception:
#         pass
#     print("[ASR] Strict grammar active:", grammar)
#     return rec


# def listen_command_exact(rec: KaldiRecognizer, stream_read, timeout_sec=COMMAND_TIMEOUT_SEC, silence_ms=FINAL_SILENCE_MS) -> str:
#     start = time.time()
#     last_voice_time = start
#     time.sleep(0.35)  # کمی بیشتر برای جدا شدن ته‌ی wake
#     try:
#         rec.Reset()
#     except Exception:
#         pass

#     exact_set = set(COMMANDS.keys())
#     best_text = ""  # آخرین متن غیرخالی که گرفتیم (صرفاً برای لاگ)

#     while True:
#         data, _ = stream_read(BLOCKSIZE)
#         if not data:
#             if time.time() - start > timeout_sec:
#                 break
#             continue

#         buf = _as_bytes(data)
#         accepted = rec.AcceptWaveform(buf)
#         now = time.time()

#         if accepted:
#             res = json.loads(rec.Result())
#             txt = (res.get("text") or "").strip()
#             if txt:
#                 best_text = txt
#                 last_voice_time = now
#                 if txt in exact_set:  # ✅ به یکی از عبارات دقیق رسیدیم
#                     return txt

#             # اگر سکوت طولانی شد و هنوز exact نشد، خروجی فعلی رو برمی‌گردونیم
#             if (now - last_voice_time) * 1000 >= silence_ms:
#                 return txt

#         else:
#             pres = json.loads(rec.PartialResult())
#             ptxt = (pres.get("partial") or "").strip()
#             if ptxt:
#                 last_voice_time = now
#                 # partial معمولاً کامل نیست؛ برای exact چک نمی‌کنیم

#         if now - start > timeout_sec:
#             break

#     # تایم‌اوت: آخرین نتیجه نهایی
#     final = json.loads(rec.FinalResult()).get("text", "").strip()
#     return final or best_text


# def main():
#     if not os.path.isdir(MODEL_PATH):
#         print(f"[FATAL] Model not found at: {MODEL_PATH}")
#         sys.exit(1)

#     print("Loading Vosk model...", MODEL_PATH)
#     model = Model(MODEL_PATH)

#     stream = sd.RawInputStream(
#         samplerate=RATE,
#         blocksize=BLOCKSIZE,
#         dtype='int16',
#         channels=CHANNELS,
#     )
#     stream.start()

#     def _sigint_handler(sig, frame):
#         print("\n[EXIT] Interrupted.")
#         try:
#             stream.stop()
#             stream.close()
#         except Exception:
#             pass
#         sys.exit(0)
#     signal.signal(signal.SIGINT, _sigint_handler)

#     print("🎤 Say something... (say 'nora' to wake)")
#     add_state_listener(_on_state_update)
#     add_control_listener(_on_control_event)
#     request_state()

#     wake_rec = build_wake_recognizer(model)
#     listening_now = False

#     def run_command_session(trigger_label: str = ""):
#         nonlocal wake_rec, listening_now
#         listening_now = True
#         try:
#             if trigger_label:
#                 print(trigger_label)
#             rec_cmd = build_command_recognizer(model)
#             cmd_text = listen_command_exact(
#                 rec_cmd,
#                 stream.read,
#                 timeout_sec=COMMAND_TIMEOUT_SEC,
#                 silence_ms=FINAL_SILENCE_MS,
#             )
#             print("📥 Full command (strict):",
#                   cmd_text if cmd_text else "<empty>")

#             matched = handle_command(cmd_text)
#             if matched:
#                 print("✅ exact command executed")
#             else:
#                 print("❌ not an exact command (ignored)")
#         finally:
#             listening_now = False
#             wake_rec = build_wake_recognizer(model)

#     while True:
#         try:
#             if _manual_listen_event.is_set() and not listening_now:
#                 _manual_listen_event.clear()
#                 run_command_session("🎧 Listening (UI request)")
#                 continue

#             data, _ = stream.read(BLOCKSIZE)
#             if not data:
#                 continue

#             buf = _as_bytes(data)                  # 👈 تبدیل قطعی به bytes
#             if not wake_word_enabled:
#                 continue

#             if wake_rec.AcceptWaveform(buf):
#                 res = json.loads(wake_rec.Result())
#                 txt = (res.get("text") or "").strip()

#                 if txt == WAKE_WORD:
#                     print(f"🔔 Wake word detected: {WAKE_WORD}")
#                     run_command_session()

#         except KeyboardInterrupt:
#             _sigint_handler(None, None)
#         except Exception as e:
#             print("[ERROR] Main loop exception:", e)
#             traceback.print_exc()
#             time.sleep(0.2)


# if __name__ == "__main__":
#     main()


import os
import sys
import json
import time
import signal
import threading
import traceback
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import socketio
from websocket_client import (
    _emit,
    add_control_listener,
    add_state_listener,
    request_state,
)

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)

# ---------- تنظیمات ASR/Audio ----------
MODEL_PATH = os.path.join(HERE, "model")
RATE = 16000
CHANNELS = 1
# blocksize پیشنهادی برای 16kHz ~100ms. در fallbackها مقادیر دیگر هم تست می‌شود.
BLOCKSIZE = 1600
DTYPE = "int16"

# ---------- تنظیمات Wake/Command ----------
WAKE_WORD = "nora"
COMMAND_TIMEOUT_SEC = 5
FINAL_SILENCE_MS = 1200

wake_word_enabled = True
_wake_lock = threading.Lock()
_manual_listen_event = threading.Event()


def _set_wake_word_enabled(enabled: bool) -> bool:
    global wake_word_enabled
    enabled = bool(enabled)
    with _wake_lock:
        if wake_word_enabled != enabled:
            wake_word_enabled = enabled
            status = "ENABLED" if enabled else "DISABLED"
            print(f"[VA] Wake word {status} via remote control")
        return wake_word_enabled


def _on_state_update(state: dict):
    try:
        va_cfg = (state or {}).get("voice_assistant", {})
        _set_wake_word_enabled(va_cfg.get("wake_word_enabled", True))
    except Exception as exc:
        print("[VA] Failed to parse state update:", exc)


def _on_control_event(message: dict):
    msg_type = (message or {}).get("type")
    if msg_type == "listen_once":
        print("[VA] Manual listen requested from UI")
        _manual_listen_event.set()
    elif msg_type == "wake_word" and "enabled" in message:
        _set_wake_word_enabled(message.get("enabled", True))


# ایمپورت پارسر
try:
    from command_parser import handle_command, COMMANDS
except Exception as e:
    print("[FATAL] Cannot import command_parser:", e)
    sys.exit(1)


# ---------- کمکی‌های صوت ----------
def _as_bytes(chunk):
    """Ensure bytes for Vosk (fix cffi buffer issue)."""
    if isinstance(chunk, (bytes, bytearray)):
        return chunk
    try:
        return memoryview(chunk).tobytes()
    except Exception:
        return bytes(chunk)


def _pick_input_device() -> int | None:
    """
    تلاش برای انتخاب ورودی Pulse؛ اگر نبود، None (یعنی default).
    """
    try:
        devs = sd.query_devices()
        # اولویت: دستگاه ورودی با نام pulse
        for i, d in enumerate(devs):
            name = str(d.get("name", "")).lower()
            if d.get("max_input_channels", 0) > 0 and "pulse" in name:
                print(f"[AUDIO] Selected input via Pulse: idx={i}, name={d['name']}")
                return i
        # اگر pulse نبود، default را بسپار به PortAudio/pipewire
        print("[AUDIO] No 'pulse' device found; using default input device.")
        return None
    except Exception as e:
        print("[AUDIO] Device query failed, falling back to default:", e)
        return None


def _open_input_stream():
    """
    استریم ورودی را با چند تلاش باز می‌کند تا با PipeWire/Pulse سازگار شود.
    """
    input_device = _pick_input_device()

    attempts = [
        dict(blocksize=BLOCKSIZE, latency="low"),
        dict(blocksize=800, latency="high"),
        dict(blocksize=None, latency="high"),  # بگذار PortAudio تصمیم بگیرد
    ]

    last_err = None
    for idx, opts in enumerate(attempts, start=1):
        try:
            stream = sd.RawInputStream(
                samplerate=RATE,
                channels=CHANNELS,
                dtype=DTYPE,
                blocksize=opts["blocksize"],
                device=input_device,  # pulse یا default
                latency=opts["latency"],
            )
            stream.start()
            print(f"[AUDIO] Input stream opened (attempt {idx}): "
                  f"device={input_device}, blocksize={opts['blocksize']}, latency={opts['latency']}")
            return stream
        except sd.PortAudioError as e:
            last_err = e
            print(f"[AUDIO] Failed to open stream (attempt {idx}): {e}")
            # کمی مکث قبل از تلاش بعدی
            time.sleep(0.15)

    print("[FATAL] Could not open input stream after retries:", last_err)
    raise last_err


# ---------- ساخت ریکاگنایزرها ----------
def build_wake_recognizer(model: Model) -> KaldiRecognizer:
    grammar = json.dumps([WAKE_WORD])
    rec = KaldiRecognizer(model, RATE, grammar)
    try:
        rec.SetWords(True)
        rec.SetMaxAlternatives(0)
    except Exception:
        pass
    print("[ASR] Wake grammar active:", grammar)
    return rec


def build_command_recognizer(model: Model) -> KaldiRecognizer:
    phrases = list(COMMANDS.keys())
    grammar = json.dumps(phrases)
    rec = KaldiRecognizer(model, RATE, grammar)
    try:
        rec.SetWords(True)
        rec.SetMaxAlternatives(0)
    except Exception:
        pass
    print("[ASR] Strict grammar active:", grammar)
    return rec


def listen_command_exact(rec: KaldiRecognizer, stream_read, timeout_sec=COMMAND_TIMEOUT_SEC, silence_ms=FINAL_SILENCE_MS) -> str:
    start = time.time()
    last_voice_time = start
    time.sleep(0.35)  # جدا شدن tail واژه بیدارباش
    try:
        rec.Reset()
    except Exception:
        pass

    exact_set = set(COMMANDS.keys())
    best_text = ""

    while True:
        data, _ = stream_read(BLOCKSIZE)
        if not data:
            if time.time() - start > timeout_sec:
                break
            continue

        buf = _as_bytes(data)
        accepted = rec.AcceptWaveform(buf)
        now = time.time()

        if accepted:
            res = json.loads(rec.Result())
            txt = (res.get("text") or "").strip()
            if txt:
                best_text = txt
                last_voice_time = now
                if txt in exact_set:
                    return txt

            if (now - last_voice_time) * 1000 >= silence_ms:
                return txt

        else:
            pres = json.loads(rec.PartialResult())
            ptxt = (pres.get("partial") or "").strip()
            if ptxt:
                last_voice_time = now

        if now - start > timeout_sec:
            break

    final = json.loads(rec.FinalResult()).get("text", "").strip()
    return final or best_text


def main():
    if not os.path.isdir(MODEL_PATH):
        print(f"[FATAL] Model not found at: {MODEL_PATH}")
        sys.exit(1)

    print("Loading Vosk model...", MODEL_PATH)
    model = Model(MODEL_PATH)

    # ---- باز کردن استریم ورودی با fallbackهای امن (Pulse/Default) ----
    stream = _open_input_stream()

    def _sigint_handler(sig, frame):
        print("\n[EXIT] Interrupted.")
        try:
            stream.stop()
            stream.close()
        except Exception:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, _sigint_handler)

    print("🎤 Say something... (say 'nora' to wake)")
    add_state_listener(_on_state_update)
    add_control_listener(_on_control_event)
    request_state()

    wake_rec = build_wake_recognizer(model)
    listening_now = False

    def run_command_session(trigger_label: str = ""):
        nonlocal wake_rec, listening_now
        listening_now = True
        try:
            if trigger_label:
                print(trigger_label)
            rec_cmd = build_command_recognizer(model)
            cmd_text = listen_command_exact(
                rec_cmd,
                stream.read,
                timeout_sec=COMMAND_TIMEOUT_SEC,
                silence_ms=FINAL_SILENCE_MS,
            )
            print("📥 Full command (strict):", cmd_text if cmd_text else "<empty>")

            matched = handle_command(cmd_text)
            if matched:
                print("✅ exact command executed")
            else:
                print("❌ not an exact command (ignored)")
        finally:
            listening_now = False
            wake_rec = build_wake_recognizer(model)

    while True:
        try:
            if _manual_listen_event.is_set() and not listening_now:
                _manual_listen_event.clear()
                run_command_session("🎧 Listening (UI request)")
                continue

            data, _ = stream.read(BLOCKSIZE)
            if not data:
                continue

            buf = _as_bytes(data)
            if not wake_word_enabled:
                continue

            if wake_rec.AcceptWaveform(buf):
                res = json.loads(wake_rec.Result())
                txt = (res.get("text") or "").strip()

                if txt == WAKE_WORD:
                    print(f"🔔 Wake word detected: {WAKE_WORD}")
                    run_command_session()

        except KeyboardInterrupt:
            _sigint_handler(None, None)
        except sd.PortAudioError as e:
            # اگر در حین کار دستگاه قطع/مشغول شد، یک‌بار استریم را با fallbackها دوباره باز کن
            print("[AUDIO] PortAudioError in main loop, reopening stream:", e)
            try:
                stream.stop()
                stream.close()
            except Exception:
                pass
            time.sleep(0.2)
            stream = _open_input_stream()
            wake_rec = build_wake_recognizer(model)
        except Exception as e:
            print("[ERROR] Main loop exception:", e)
            traceback.print_exc()
            time.sleep(0.2)


if __name__ == "__main__":
    main()
