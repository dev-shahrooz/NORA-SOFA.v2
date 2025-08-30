# nora/app.py
import os
from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit

from core.state_store import StateStore
from core.event_bus import EventBus
from core.action_router import ActionRouter
from core.usecases.lighting import LightingService
from core.usecases.audio import AudioUsecase
from core.usecases.relay import SingleRelayUsecase
from core.usecases.mode import ModeUsecase
from services.audio_service import AudioService
from drivers.esp32_link import ESP32Link
from drivers.gpio_driver import GPIODriver                    

DB_PATH = os.environ.get("NORA_DB","C:/Users/Shahrooz/Desktop/nora-sofa-core/nora/data/nora.db")

app = Flask(__name__, static_folder="ui", static_url_path="/ui")
sio = SocketIO(app, cors_allowed_origins="*")

OPEN_BOX_PIN = 22
CLOSE_BOX_PIN = 23
PARTY_MODE_AMP_PIN = 24
READING_LIGHT_PIN = 17
BACK_LIGHT_PIN = 18


state = StateStore(DB_PATH)
bus = EventBus()
esp = ESP32Link(port=os.environ.get("ESP_PORT","/dev/ttyUSB0"))
lighting = LightingService(esp)
audio_service = AudioService()
audio_uc = AudioUsecase(audio_service)
# --- GPIO / Reading Light wiring ---
READING_LIGHT = int(os.environ.get("READING_LIGHT_PIN", READING_LIGHT_PIN))
ACTIVE_LOW_READING_LIGHT = (os.environ.get("READING_LIGHT_ACTIVE_LOW", "0") == "1")
BACK_LIGHT = int(os.environ.get("BACK_LIGHT_PIN", BACK_LIGHT_PIN))
ACTIVE_LOW_BACK_LIGHT = (os.environ.get("BACK_LIGHT_ACTIVE_LOW", "0") == "1")
gpio = GPIODriver(chip=0)  # /dev/gpiochip0

open_box_uc = int(os.environ.get("OPEN_BOX_PIN", OPEN_BOX_PIN))
close_box_uc = int(os.environ.get("CLOSE_RELAY_PIN", CLOSE_BOX_PIN))
party_mode_amp_uc = int(os.environ.get("PARTY_MUTE_PIN", PARTY_MODE_AMP_PIN))
reading_light_uc = SingleRelayUsecase(gpio_driver=gpio, name="reading_light", pin=READING_LIGHT, active_low=ACTIVE_LOW_READING_LIGHT)
back_light_uc = SingleRelayUsecase(gpio, name="back_light", pin=BACK_LIGHT, active_low=ACTIVE_LOW_BACK_LIGHT)
mode_uc = ModeUsecase(
    state,
    lighting,
    audio_uc,
    reading_light_uc,
    back_light_uc,
    gpio,
    open_box_uc,
    close_box_uc,
    party_mode_amp_uc,
)
router = ActionRouter(state, lighting, audio_uc, reading_light_uc, back_light_uc, mode_uc)


@app.route("/")
def index():
    return send_from_directory("ui", "index.html")

@sio.on("ui.query")
def on_query(data):
    emit("sv.update", state.get_state())

@sio.on("ui.intent")
def on_intent(data):
    action = data.get("type","?")
    payload = data.get("payload",{})
    new_state = router.handle(source="lcd", action=action, payload=payload, corr_id=data.get("corr_id",""))
    emit("sv.update", new_state, broadcast=True)

if __name__ == "__main__":
    sio.run(app, host="0.0.0.0", port=8080)