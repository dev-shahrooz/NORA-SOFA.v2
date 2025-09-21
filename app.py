# nora/app.py
import os
from typing import Any, Dict
from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit

from core.state_store import StateStore
from core.event_bus import EventBus
from core.action_router import ActionRouter
from core.usecases.lighting import LightingService
from core.usecases.reading_light import ReadingLightUsecase
from core.usecases.back_light import BackLightUsecase
from core.usecases.mode import ModeUsecase
from core.usecases.bluetooth import BluetoothUsecase
from core.usecases.audio import AudioUsecase
from core.usecases.player import PlayerUsecase
from core.usecases.wifi import WiFiUsecase
from services.bluetooth_service import BluetoothService
from services.audio_service import AudioService
from services.player_service import PlayerService
from services.wifi_service import WiFiService
from drivers.esp32_link import ESP32Link

DB_PATH = os.environ.get("NORA_DB","/home/nora/apps/NORA-SOFA.v2/data/nora.db")

app = Flask(__name__, static_folder="ui", static_url_path="/ui")
sio = SocketIO(app, cors_allowed_origins="*")


state = StateStore(DB_PATH)
bus = EventBus()
esp = ESP32Link(port=os.environ.get("ESP_PORT","/dev/ttyUSB0"))
lighting = LightingService(esp)
bt_service = BluetoothService()
bluetooth_uc = BluetoothUsecase(bt_service)
audio_service = AudioService()
audio_uc = AudioUsecase(audio_service, esp, state)
player_service = PlayerService()
player_uc = PlayerUsecase(player_service)
wifi_service = WiFiService()
wifi_uc = WiFiUsecase(wifi_service)
reading_light_uc = ReadingLightUsecase(esp)
back_light_uc = BackLightUsecase(esp)
mode_uc = ModeUsecase(
    state,
    lighting,
    esp,
)
router = ActionRouter(state, lighting, reading_light_uc, back_light_uc, mode_uc, bluetooth_uc, audio_uc, player_uc, wifi_uc)

def _apply_state_to_hardware(s: Dict[str, Any]) -> None:
    """Apply persisted state to physical hardware without mutating DB."""
    lighting_state = s.get("lighting", {})
    for zone in ("under_sofa", "box"):
        z = lighting_state.get(zone)
        if not z:
            continue
        try:
            lighting.set_zone(
                zone,
                z.get("mode", "off"),
                z.get("color", "#ffffff"),
                z.get("brightness", "mid"),
            )
        except Exception:
            pass
    try:
        rl = lighting_state.get("reading_light", {})
        reading_light_uc.set(bool(rl.get("on")))
    except Exception:
        pass
    try:
        bl = lighting_state.get("back_light", {})
        back_light_uc.set(bool(bl.get("on")))
    except Exception:
        pass
    try:
        bluetooth_uc.set(bool(s.get("bluetooth", {}).get("on", True)))
    except Exception:
        pass
    try:
        wifi_uc.set(bool(s.get("wifi", {}).get("on", True)))
    except Exception:
        pass
    try:
        vol = int(s.get("audio", {}).get("volume", 50))
        audio_uc.set_volume(vol)
        muted = bool(s.get("audio", {}).get("muted", False))
        audio_uc.set_mute(muted)
    except Exception:
        pass

def sync_hardware_from_state() -> None:
    """Load last state from DB and broadcast it."""
    current = state.get_state()
    _apply_state_to_hardware(current)
    try:
        patch = player_uc.info()
        current = state.apply_patch(patch, source="system", action="player.info", payload={})
        sio.emit("sv.update", current)
    except Exception:
        pass


sync_hardware_from_state()


@app.route("/")
def index():
    return send_from_directory("ui", "index.html")

@sio.on("ui.query")
def on_query(data):
    patch = player_uc.info()
    st = state.apply_patch(patch, source="ui", action="player.info", payload={})
    emit("sv.update", st)
    
@sio.on("ui.intent")
def on_intent(data):
    action = data.get("type","?")
    payload = data.get("payload",{})
    new_state = router.handle(source="lcd", action=action, payload=payload, corr_id=data.get("corr_id",""))
    emit("sv.update", new_state, broadcast=True)

if __name__ == "__main__":
    sio.run(app, host="0.0.0.0", port=8080)