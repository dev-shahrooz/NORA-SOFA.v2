# بالا:
from typing import Dict
# + از مرحله قبل:
# from nora.core.usecases.reading_light import ReadingLightUsecase  # تزریق از app.py انجام می‌شود

class ActionRouter:
    def __init__(
        self,
        state_store,
        lighting_uc,
        reading_light_uc,
        back_light_uc,
        mode_uc,
        bluetooth_uc,
        audio_uc,
        player_uc,
        wifi_uc,
        clock_uc,
    ):        
        self.state_store = state_store
        self.lighting = lighting_uc
        self.reading_light = reading_light_uc
        self.back_light = back_light_uc
        self.mode = mode_uc
        self.bluetooth = bluetooth_uc
        self.audio = audio_uc
        self.player = player_uc
        self.wifi = wifi_uc
        self.clock = clock_uc


    def handle(self, source: str, action: str, payload: Dict, corr_id: str = "") -> Dict:
        patch = {}

        # --- Lighting (قدیمی) ---
        if action == "lighting.set":
            patch = self.lighting.set_zone(
                zone=payload.get("zone", "under_sofa"),
                mode=payload.get("mode", "off"),
                color=payload.get("color", "#FFFFFF"),
                brightness=payload.get("brightness", "mid"),
            )

        # --- Reading Light (جدید) ---
        elif action == "reading_light.set":
            want_on = bool(payload.get("on"))
            patch = self.reading_light.set(want_on)

        elif action == "reading_light.toggle":
            # از state فعلی بخوانیم:
            current = self.state_store.get_state()
            current_on = bool(current.get("lighting", {}).get("reading_light", {}).get("on", False))
            patch = self.reading_light.toggle(current_on)

        # --- Back Light (جدید) ---
        elif action == "back_light.set":
            want_on = bool(payload.get("on"))
            patch = self.back_light.set(want_on)

        elif action == "back_light.toggle":
            # از state فعلی بخوانیم:
            current = self.state_store.get_state()
            current_on = bool(current.get("lighting", {}).get("back_light", {}).get("on", False))
            patch = self.back_light.toggle(current_on)
        
        # --- Bluetooth Power ---
        elif action == "bluetooth.set":
            want_on = bool(payload.get("on"))
            patch = self.bluetooth.set(want_on)

        elif action == "bluetooth.toggle":
            current = self.state_store.get_state()
            current_on = bool(current.get("bluetooth", {}).get("on", False))
            patch = self.bluetooth.toggle(current_on)

        # --- Bluetooth unpair ---
        elif action == "bluetooth.unpair":
            patch = self.bluetooth.unpair()

         # --- Wi-Fi Power ---
        elif action == "wifi.set":
            want_on = bool(payload.get("on"))
            patch = self.wifi.set(want_on)

        elif action == "wifi.toggle":
            current = self.state_store.get_state()
            current_on = bool(current.get("wifi", {}).get("on", False))
            patch = self.wifi.toggle(current_on)

        # --- Wi-Fi Scan ---
        elif action == "wifi.scan":
            patch = self.wifi.scan()

        # --- Wi-Fi Connect ---
        elif action == "wifi.connect":
            ssid = payload.get("ssid", "")
            password = payload.get("password", "")
            patch = self.wifi.connect(ssid, password)

        # --- Wi-Fi Forget ---
        elif action == "wifi.forget":
            ssid = payload.get("ssid", "")
            patch = self.wifi.forget(ssid)


        # --- Audio Volume ---
        elif action == "audio.set_volume":
            vol = int(payload.get("volume", 0))
            patch = self.audio.set_volume(vol)
        elif action == "audio.set_mute":
            mute = bool(payload.get("mute", False))
            patch = self.audio.set_mute(mute)
        # --- Media Player Controls ---
        elif action == "player.play":
            patch = self.player.play()

        elif action == "player.pause":
            patch = self.player.pause()

        elif action == "player.next":
            patch = self.player.next()

        elif action == "player.previous":
            patch = self.player.previous()

        elif action == "player.info":
            patch = self.player.info()

        # --- Mode Toggle ---
        elif action == "mode.toggle":
            patch = self.mode.toggle()
        # Mode Set
        elif action == "mode.set":
            patch = self.mode.set(payload.get("mode"))

        elif action == "ui.set_lang":
            lang = payload.get("lang", "en")
            patch = {"lang": lang}

        # --- Clock ---
        elif action == "clock.set_time":
            try:
                patch = self.clock.set_time(
                    hour=payload.get("hour"),
                    minute=payload.get("minute"),
                    second=payload.get("second"),
                    time_str=payload.get("time"),
                )
            except ValueError:
                patch = {}

        # --- Default ---
        else:
            patch = {}

        if patch:
            return self.state_store.apply_patch(
                patch, source=source, action=action, payload=payload, corr_id=corr_id
            )
        else:
            return self.state_store.get_state()
