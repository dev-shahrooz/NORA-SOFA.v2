const sio = io();

function send(type, payload = {}) {
  sio.emit("ui.intent", { type, payload, corr_id: String(Date.now()) });
}

const translations = {
  fa: {
    reading_light_title: "چراغ مطالعه",
    reading_light_turn_on: "روشن کردن چراغ",
    reading_light_turn_off: "خاموش کردن چراغ",
    status_on: "روشن",
    status_off: "خاموش",
    back_light_title: "چراغ پشت (Back Light)",
    back_light_turn_on: "روشن کردن چراغ پشت",
    back_light_turn_off: "خاموش کردن چراغ پشت",
    party_mode: "Party Mode",
    under_sofa_title: "نور زیر مبل",
    zone_label: "زون:",
    zone_under_sofa: "زیر مبل",
    zone_box: "باکس",
    mode_label: "حالت:",
    mode_off: "خاموش",
    mode_rainbow: "رینبو",
    mode_static: "رنگ ثابت",
    mode_eq: "اکولایزر",
    color_label: "رنگ:",
    brightness_label: "روشنایی:",
    apply_light: "ثبت",
    bluetooth_title: "بلوتوث سیستم",
    bluetooth_turn_on: "روشن کردن بلوتوث",
    bluetooth_turn_off: "خاموش کردن بلوتوث",
    bluetooth_unpair: "Unpair Bluetooth",
    wifi_title: "وای‌فای",
    wifi_turn_on: "روشن کردن وای‌فای",
    wifi_turn_off: "خاموش کردن وای‌فای",
    wifi_scan: "جستجو شبکه‌ها",
    wifi_forget: "فراموش کردن",
    wifi_connected_label: "اتصال فعلی:",
    wifi_saved_label: "شبکه‌های ذخیره‌شده",
    wifi_saved_current: "متصل",
    wifi_password_prompt: "رمز برای {ssid}:",
    wifi_fail_prompt: "اتصال ناموفق بود. رمز را دوباره وارد کنید برای {ssid}:",
    volume_title: "حجم صدا",
    sound_turn_off: "قطع صدا",
    sound_turn_on: "وصل صدا",
    media_player_title: "مدیا پلیر",
    player_prev: "قبلی",
    player_play: "پلی",
    player_pause: "پاز",
    player_next: "بعدی",
  },
  en: {
    reading_light_title: "Reading Light",
    reading_light_turn_on: "Turn on light",
    reading_light_turn_off: "Turn off light",
    status_on: "On",
    status_off: "Off",
    back_light_title: "Back Light",
    back_light_turn_on: "Turn on back light",
    back_light_turn_off: "Turn off back light",
    party_mode: "Party Mode",
    under_sofa_title: "Under-sofa Lights",
    zone_label: "Zone:",
    zone_under_sofa: "Under sofa",
    zone_box: "Box",
    mode_label: "Mode:",
    mode_off: "Off",
    mode_rainbow: "Rainbow",
    mode_static: "Static color",
    mode_eq: "Equalizer",
    color_label: "Color:",
    brightness_label: "Brightness:",
    apply_light: "Apply",
    bluetooth_title: "System Bluetooth",
    bluetooth_turn_on: "Turn on Bluetooth",
    bluetooth_turn_off: "Turn off Bluetooth",
    bluetooth_unpair: "Unpair Bluetooth",
    wifi_title: "Wi-Fi",
    wifi_turn_on: "Turn on Wi-Fi",
    wifi_turn_off: "Turn off Wi-Fi",
    wifi_scan: "Scan Networks",
    wifi_forget: "Forget",
    wifi_connected_label: "Currently connected:",
    wifi_saved_label: "Saved networks",
    wifi_saved_current: "Currently connected",
    wifi_password_prompt: "Password for {ssid}:",
    wifi_fail_prompt: "Connection failed. Enter password again for {ssid}:",
    volume_title: "Volume",
    sound_turn_off: "Mute sound",
    sound_turn_on: "Unmute sound",
    media_player_title: "Media Player",
    player_prev: "Previous",
    player_play: "Play",
    player_pause: "Pause",
    player_next: "Next",
  },
  tr: {
    reading_light_title: "Okuma Lambası",
    reading_light_turn_on: "Lambayı aç",
    reading_light_turn_off: "Lambayı kapat",
    status_on: "Açık",
    status_off: "Kapalı",
    back_light_title: "Arka Işık",
    back_light_turn_on: "Arka ışığı aç",
    back_light_turn_off: "Arka ışığı kapat",
    party_mode: "Parti Modu",
    under_sofa_title: "Koltuk Altı Işıkları",
    zone_label: "Bölge:",
    zone_under_sofa: "Koltuk altı",
    zone_box: "Kutu",
    mode_label: "Mod:",
    mode_off: "Kapalı",
    mode_rainbow: "Gökkuşağı",
    mode_static: "Sabit renk",
    mode_eq: "Ekolayzır",
    color_label: "Renk:",
    brightness_label: "Parlaklık:",
    apply_light: "Uygula",
    bluetooth_title: "Sistem Bluetooth'u",
    bluetooth_turn_on: "Bluetooth'u aç",
    bluetooth_turn_off: "Bluetooth'u kapat",
    bluetooth_unpair: "Bluetooth eşlemesini kaldır",
    wifi_title: "Wi-Fi",
    wifi_turn_on: "Wi-Fi'yi aç",
    wifi_turn_off: "Wi-Fi'yi kapat",
    wifi_scan: "Ağları Tara",
    wifi_forget: "Unut",
    wifi_connected_label: "Bağlı ağ:",
    wifi_saved_label: "Kaydedilmiş ağlar",
    wifi_saved_current: "Şu an bağlı",
    wifi_password_prompt: "{ssid} için parola:",
    wifi_fail_prompt: "Bağlantı başarısız. {ssid} için parolayı tekrar girin:",
    volume_title: "Ses",
    sound_turn_off: "Sesi kapat",
    sound_turn_on: "Sesi aç",
    media_player_title: "Medya Oynatıcı",
    player_prev: "Önceki",
    player_play: "Oynat",
    player_pause: "Duraklat",
    player_next: "Sonraki",
  },
  ar: {
    reading_light_title: "مصباح القراءة",
    reading_light_turn_on: "تشغيل المصباح",
    reading_light_turn_off: "إيقاف المصباح",
    status_on: "تشغيل",
    status_off: "إيقاف",
    back_light_title: "الإضاءة الخلفية",
    back_light_turn_on: "تشغيل الإضاءة الخلفية",
    back_light_turn_off: "إيقاف الإضاءة الخلفية",
    party_mode: "وضع الحفلة",
    under_sofa_title: "إضاءة تحت الأريكة",
    zone_label: "منطقة:",
    zone_under_sofa: "تحت الأريكة",
    zone_box: "الصندوق",
    mode_label: "وضع:",
    mode_off: "إيقاف",
    mode_rainbow: "قوس قزح",
    mode_static: "لون ثابت",
    mode_eq: "موازن",
    color_label: "لون:",
    brightness_label: "السطوع:",
    apply_light: "تطبيق",
    bluetooth_title: "بلوتوث النظام",
    bluetooth_turn_on: "تشغيل البلوتوث",
    bluetooth_turn_off: "إيقاف البلوتوث",
    bluetooth_unpair: "إلغاء اقتران البلوتوث",
    wifi_title: "واي فاي",
    wifi_turn_on: "تشغيل الواي فاي",
    wifi_turn_off: "إيقاف الواي فاي",
    wifi_scan: "مسح الشبكات",
    wifi_forget: "نسيان",
    wifi_connected_label: "الشبكة المتصلة:",
    wifi_saved_label: "الشبكات المحفوظة",
    wifi_saved_current: "متصل الآن",
    wifi_password_prompt: "كلمة المرور لـ {ssid}:",
    wifi_fail_prompt: "فشل الاتصال. أدخل كلمة المرور مرة أخرى لـ {ssid}:",
    volume_title: "مستوى الصوت",
    sound_turn_off: "إيقاف الصوت",
    sound_turn_on: "تشغيل الصوت",
    media_player_title: "مشغل الوسائط",
    player_prev: "السابق",
    player_play: "تشغيل",
    player_pause: "إيقاف مؤقت",
    player_next: "التالي",
  },
};

let currentLang = "fa";
let lastState = {};

function t(key, vars = {}) {
  let str = translations[currentLang][key] || key;
  Object.keys(vars).forEach((k) => {
    str = str.replace(`{${k}}`, vars[k]);
  });
  return str;
}

function applyTranslations() {
  document.documentElement.lang = currentLang;
  document.documentElement.dir = ["fa", "ar"].includes(currentLang)
    ? "rtl"
    : "ltr";
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    el.textContent = t(key);
  });
  renderReadingLight(lastState);
  renderBackLight(lastState);
  renderPartyMode(lastState);
  renderLightingInputs(lastState);
  renderBluetooth(lastState);
  renderWiFi(lastState);
  renderVolume(lastState);
  renderPlayer(lastState);
}

function setLang(lang) {
  currentLang = lang;
  applyTranslations();
  send("ui.set_lang", { lang });
}

// ---- UI Elements ----
const langSelect = document.getElementById("lang-select");
const readingBtn = document.getElementById("reading-toggle");
const readingStatus = document.getElementById("reading-status");
const backBtn = document.getElementById("back-toggle");
const backStatus = document.getElementById("back-status");
const partyBtn = document.getElementById("party-toggle");
const zoneSelect = document.getElementById("zone");
const modeSelect = document.getElementById("mode");
const colorInput = document.getElementById("color");
const brightnessInput = document.getElementById("brightness");
const btBtn = document.getElementById("bt-toggle");
const btStatus = document.getElementById("bt-status");
const wifiBtn = document.getElementById("wifi-toggle");
const wifiStatus = document.getElementById("wifi-status");
const wifiScanBtn = document.getElementById("wifi-scan");
const wifiList = document.getElementById("wifi-networks");
const wifiSSID = document.getElementById("wifi-ssid");
const wifiForgetCurrentBtn = document.getElementById("wifi-forget-current");
const wifiConnected = document.querySelector(".wifi-connected");
const wifiSavedContainer = document.querySelector(".wifi-saved");
const wifiSavedSelect = document.getElementById("wifi-saved-select");
const wifiSavedForgetBtn = document.getElementById("wifi-saved-forget");
let pendingSSID = null;
let wifiScanRequested = false;
const volumeRange = document.getElementById("volume");
const volumeValue = document.getElementById("volume-value");
const muteBtn = document.getElementById("mute-toggle");
const playBtn = document.getElementById("player-play");
const pauseBtn = document.getElementById("player-pause");
const nextBtn = document.getElementById("player-next");
const prevBtn = document.getElementById("player-prev");
const trackTitle = document.getElementById("track-title");
const trackArtist = document.getElementById("track-artist");

// ---- Rendering Functions ----
function renderReadingLight(st) {
  const on = !!st?.lighting?.reading_light?.on;
  if (on) {
    readingBtn.textContent = t("reading_light_turn_off");
    readingBtn.classList.add("on");
    readingStatus.textContent = t("status_on");
    readingStatus.classList.add("on");
  } else {
    readingBtn.textContent = t("reading_light_turn_on");
    readingBtn.classList.remove("on");
    readingStatus.textContent = t("status_off");
    readingStatus.classList.remove("on");
  }
}

function renderPartyMode(st) {
  const active = st.mode === "party";
  if (active) {
    partyBtn.classList.add("on");
  } else {
    partyBtn.classList.remove("on");
  }
}

function renderBluetooth(st) {
  const on = !!st?.bluetooth?.on;
  if (on) {
    btBtn.textContent = t("bluetooth_turn_off");
    btBtn.classList.add("on");
    btStatus.textContent = t("status_on");
    btStatus.classList.add("on");
  } else {
    btBtn.textContent = t("bluetooth_turn_on");
    btBtn.classList.remove("on");
    btStatus.textContent = t("status_off");
    btStatus.classList.remove("on");
  }
}

function renderWiFi(st) {
  const wifi = st?.wifi || {};
  const on = !!wifi.on;
  if (on) {
    wifiBtn.textContent = t("wifi_turn_off");
    wifiBtn.classList.add("on");
    wifiStatus.textContent = t("status_on");
    wifiStatus.classList.add("on");
    wifiScanBtn.disabled = false;
    if (!wifiScanRequested && !wifi.networks) {
      wifiScanRequested = true;
      send("wifi.scan");
    }
  } else {
    wifiBtn.textContent = t("wifi_turn_on");
    wifiBtn.classList.remove("on");
    wifiStatus.textContent = t("status_off");
    wifiStatus.classList.remove("on");
    wifiScanBtn.disabled = true;
    wifiScanRequested = false;
  }

  // Connected network
  const isConnected = !!wifi.connected && !!wifi.ssid;
  if (wifiConnected) {
    if (isConnected) {
      wifiSSID.textContent = wifi.ssid || "";
      if (wifiForgetCurrentBtn) {
        wifiForgetCurrentBtn.style.display = "inline";
        wifiForgetCurrentBtn.disabled = false;
      }
      wifiConnected.style.display = "flex";
    } else {
      wifiSSID.textContent = "";
      if (wifiForgetCurrentBtn) {
        wifiForgetCurrentBtn.style.display = "none";
      }
      wifiConnected.style.display = "none";
    }
  }

  if (wifiSavedContainer && wifiSavedSelect) {
    const savedRaw = Array.isArray(wifi.saved_networks)
      ? wifi.saved_networks
      : [];
    const saved = savedRaw
      .filter(
        (net) => net && typeof net.ssid === "string" && net.ssid.trim() !== ""
      )
      .map((net) => ({ ssid: net.ssid.trim(), active: !!net.active }));
    const previousSelection = wifiSavedSelect.value;
    wifiSavedSelect.innerHTML = "";
    saved.forEach((net) => {
      const option = document.createElement("option");
      option.value = net.ssid;
      let label = net.ssid;
      if (net.active) {
        label += ` (${t("wifi_saved_current")})`;
      }
      option.textContent = label;
      wifiSavedSelect.appendChild(option);
    });

    if (saved.length > 0) {
      let nextValue =
        previousSelection && saved.some((net) => net.ssid === previousSelection)
          ? previousSelection
          : "";
      if (!nextValue) {
        const activeNet = saved.find((net) => net.active && net.ssid);
        nextValue = activeNet?.ssid || saved[0].ssid;
      }
      wifiSavedSelect.value = nextValue;
      wifiSavedContainer.style.display = "flex";
      if (wifiSavedForgetBtn) {
        wifiSavedForgetBtn.disabled = !nextValue;
      }
    } else {
      wifiSavedContainer.style.display = "none";
      wifiSavedSelect.value = "";
      if (wifiSavedForgetBtn) {
        wifiSavedForgetBtn.disabled = true;
      }
    }
  }

  // Render network list
  wifiList.innerHTML = "";
  (wifi.networks || []).forEach((net) => {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    const isActive = wifi.ssid && net.ssid === wifi.ssid;
    btn.textContent = isActive
      ? `${net.ssid} (${net.signal}) • ${t("wifi_saved_current")}`
      : `${net.ssid} (${net.signal})`;
    btn.className = "btn";
    btn.onclick = () => connectSSID(net.ssid);
    li.appendChild(btn);
    wifiList.appendChild(li);
  });

  // handle pending connection result
  const attempt = wifi.last_connection_attempt;
  if (pendingSSID && attempt && attempt.ssid === pendingSSID) {
    if (attempt.success) {
      pendingSSID = null;
    } else {
      const pwd = prompt(t("wifi_fail_prompt", { ssid: pendingSSID }));
      if (pwd !== null) {
        send("wifi.connect", { ssid: pendingSSID, password: pwd });
      } else {
        pendingSSID = null;
      }
    }
  }
}

function renderVolume(st) {
  const vol = st?.audio?.volume ?? 0;
  volumeRange.value = vol;
  volumeValue.textContent = vol;
  const muted = !!st?.audio?.muted;
  if (muted) {
    muteBtn.textContent = t("sound_turn_on");
    muteBtn.classList.add("on");
  } else {
    muteBtn.textContent = t("sound_turn_off");
    muteBtn.classList.remove("on");
  }
}

function renderPlayer(st) {
  const p = st?.player || {};
  trackTitle.textContent = p.title || "";
  trackArtist.textContent = p.artist || "";
}

function renderBackLight(st) {
  const on = !!st?.lighting?.back_light?.on;
  if (on) {
    backBtn.textContent = t("back_light_turn_off");
    backBtn.classList.add("on");
    backStatus.textContent = t("status_on");
    backStatus.classList.add("on");
  } else {
    backBtn.textContent = t("back_light_turn_on");
    backBtn.classList.remove("on");
    backStatus.textContent = t("status_off");
    backStatus.classList.remove("on");
  }
}

function sanitizeMode(mode) {
  const allowed = new Set(["off", "rainbow", "static", "eq"]);
  return allowed.has(mode) ? mode : "off";
}

function sanitizeColor(color) {
  if (typeof color !== "string") {
    return "#ffffff";
  }
  const trimmed = color.trim();
  if (/^#[0-9A-Fa-f]{6}$/.test(trimmed)) {
    return trimmed.toLowerCase();
  }
  const hex = trimmed.replace(/[^0-9A-Fa-f]/g, "").slice(0, 6);
  return hex.length === 6 ? `#${hex.toLowerCase()}` : "#ffffff";
}

function sanitizeBrightness(brightness) {
  const value = Number(brightness);
  if (!Number.isFinite(value)) {
    return 128;
  }
  return Math.min(255, Math.max(0, Math.round(value)));
}

function renderLightingInputs(st) {
  if (!zoneSelect || !modeSelect || !colorInput || !brightnessInput) {
    return;
  }
  const zone = zoneSelect.value || "under_sofa";
  const lighting = st?.lighting || {};
  const zoneState = lighting[zone] || {};
  const mode = sanitizeMode(zoneState.mode);
  if (modeSelect.value !== mode) {
    modeSelect.value = mode;
  }
  const color = sanitizeColor(zoneState.color);
  if (colorInput.value.toLowerCase() !== color) {
    colorInput.value = color;
  }
  const brightness = sanitizeBrightness(zoneState.brightness);
  if (sanitizeBrightness(brightnessInput.value) !== brightness) {
    brightnessInput.value = String(brightness);
  }
  colorInput.disabled = mode !== "static";
}

// ---- Event Handlers ----
readingBtn.onclick = () => {
  const next = !readingStatus.classList.contains("on");
  send("reading_light.set", { on: next });
};

partyBtn.onclick = () => {
  send("mode.toggle");
};

btBtn.onclick = () => {
  const next = !btStatus.classList.contains("on");
  send("bluetooth.set", { on: next });
};

wifiBtn.onclick = () => {
  const next = !wifiStatus.classList.contains("on");
  send("wifi.set", { on: next });
};

wifiScanBtn.onclick = () => send("wifi.scan");

if (wifiForgetCurrentBtn) {
  wifiForgetCurrentBtn.onclick = () => {
    const ssid = wifiSSID.textContent;
    if (ssid) {
      send("wifi.forget", { ssid });
    }
  };
}

if (wifiSavedSelect) {
  wifiSavedSelect.onchange = () => {
    if (wifiSavedForgetBtn) {
      wifiSavedForgetBtn.disabled = !wifiSavedSelect.value;
    }
  };
}

if (wifiSavedForgetBtn) {
  wifiSavedForgetBtn.onclick = () => {
    const ssid = wifiSavedSelect?.value || "";
    if (ssid) {
      send("wifi.forget", { ssid });
    }
  };
}


if (zoneSelect) {
  zoneSelect.onchange = () => {
    renderLightingInputs(lastState);
  };
}

if (modeSelect && colorInput) {
  modeSelect.onchange = () => {
    colorInput.disabled = modeSelect.value !== "static";
  };
}

function connectSSID(ssid) {
  const pwd = prompt(t("wifi_password_prompt", { ssid }));
  if (pwd !== null) {
    pendingSSID = ssid;
    send("wifi.connect", { ssid, password: pwd });
  }
}

playBtn.onclick = () => send("player.play");
pauseBtn.onclick = () => send("player.pause");
nextBtn.onclick = () => send("player.next");
prevBtn.onclick = () => send("player.previous");

backBtn.onclick = () => {
  const next = !backStatus.classList.contains("on");
  send("back_light.set", { on: next });
};

muteBtn.onclick = () => {
  const next = !muteBtn.classList.contains("on");
  send("audio.set_mute", { mute: next });
};

// Query initial state
sio.emit("ui.query", {});

sio.on("sv.update", (st) => {
  lastState = st;
  if (st.lang && st.lang !== currentLang) {
    currentLang = st.lang;
    if (langSelect) {
      langSelect.value = currentLang;
    }
    applyTranslations();
  }
  renderReadingLight(st);
  renderBackLight(st);
  renderPartyMode(st);
  renderLightingInputs(st);
  renderBluetooth(st);
  renderWiFi(st);
  renderVolume(st);
  renderPlayer(st);
});

// Lighting apply
document.getElementById("apply-light").onclick = () => {
  const zone = zoneSelect?.value || "under_sofa";
  const mode = sanitizeMode(modeSelect?.value);
  const color = sanitizeColor(colorInput?.value);
  const brightness = sanitizeBrightness(brightnessInput?.value);
  if (colorInput) {
    colorInput.value = color;
  }
  if (brightnessInput) {
    brightnessInput.value = String(brightness);
  }
  send("lighting.set", { zone, mode, color, brightness });
};

// Unpairing
document.getElementById("unpair").onclick = () => {
  send("bluetooth.unpair");
};

volumeRange.oninput = () => {
  const vol = +volumeRange.value;
  volumeValue.textContent = vol;
  console.log("Volume set to:", vol);
  send("audio.set_volume", { volume: vol });
};

// Initialize language selector and translations
if (langSelect) {
  langSelect.value = currentLang;
  langSelect.onchange = (e) => setLang(e.target.value);
}
applyTranslations();
