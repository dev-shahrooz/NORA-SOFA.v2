const sio = io();

function send(type, payload = {}) {
  sio.emit("ui.intent", { type, payload, corr_id: String(Date.now()) });
}

// ---- Reading Light: Toggle ----
const readingBtn = document.getElementById("reading-toggle");
const readingStatus = document.getElementById("reading-status");

function renderReadingLight(st) {
  const on = !!st?.lighting?.reading_light?.on;
  if (on) {
    readingBtn.textContent = "خاموش کردن چراغ";
    readingBtn.classList.add("on");
    readingStatus.textContent = "روشن";
    readingStatus.classList.add("on");
  } else {
    readingBtn.textContent = "روشن کردن چراغ";
    readingBtn.classList.remove("on");
    readingStatus.textContent = "خاموش";
    readingStatus.classList.remove("on");
  }
}

readingBtn.onclick = () => {
  const next = !(readingStatus.textContent === "روشن");
  send("reading_light.set", { on: next });
};

// ---- Back Light: Toggle via set(on:bool) ----
const backBtn = document.getElementById("back-toggle");
const backStatus = document.getElementById("back-status");
// ---- Party Mode Toggle ----
const partyBtn = document.getElementById("party-toggle");
// ---- Bluetooth Power Toggle ----
const btBtn = document.getElementById("bt-toggle");
const btStatus = document.getElementById("bt-status");

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
    btBtn.textContent = "خاموش کردن بلوتوث";
    btBtn.classList.add("on");
    btStatus.textContent = "روشن";
    btStatus.classList.add("on");
  } else {
    btBtn.textContent = "روشن کردن بلوتوث";
    btBtn.classList.remove("on");
    btStatus.textContent = "خاموش";
    btStatus.classList.remove("on");
  }
}

partyBtn.onclick = () => {
  send("mode.toggle");
};

btBtn.onclick = () => {
  const next = !(btStatus.textContent === "روشن");
  send("bluetooth.set", { on: next });
};


function renderBackLight(st) {
  const on = !!st?.lighting?.back_light?.on;
  if (on) {
    backBtn.textContent = "خاموش کردن چراغ پشت";
    backBtn.classList.add("on");
    backStatus.textContent = "روشن";
    backStatus.classList.add("on");
  } else {
    backBtn.textContent = "روشن کردن چراغ پشت";
    backBtn.classList.remove("on");
    backStatus.textContent = "خاموش";
    backStatus.classList.remove("on");
  }
}

backBtn.onclick = () => {
  const next = !(backStatus.textContent === "روشن");
  send("back_light.set", { on: next });
};

// Query initial state
sio.emit("ui.query", {});

sio.on("sv.update", (st) => {
  const t = document.getElementById("track");
  const a = st.audio || {};
  t.textContent = a.title
    ? `${a.title} — ${a.artist}`
    : a.source === "spotify"
    ? "Spotify"
    : "Bluetooth";
  document.getElementById("volume").value = a.volume ?? 70;
  renderReadingLight(st);
  renderBackLight(st);
  renderPartyMode(st);
  renderBluetooth(st);
});

// Lighting apply
document.getElementById("apply-light").onclick = () => {
  const zone = document.getElementById("zone").value;
  const mode = document.getElementById("mode").value;
  const color = document.getElementById("color").value;
  const brightness = +document.getElementById("brightness").value;
  send("lighting.set", { zone, mode, color, brightness });
};

// Source set
document.getElementById("set-source").onclick = () => {
  const src = [...document.querySelectorAll('input[name="source"]')].find(
    (x) => x.checked
  ).value;
  send("audio.set_source", { source: src });
};

// Pairing
document.getElementById("pair").onclick = () => {
  fetch("/api/pair", { method: "POST" }).catch(() => {});
  alert("Pairing window opened for 120s");
};

// Mini-player controls
document.getElementById("play").onclick = () =>
  send("audio.command", { op: "play_pause" });

document.getElementById("next").onclick = () =>
  send("audio.command", { op: "next" });

document.getElementById("prev").onclick = () =>
  send("audio.command", { op: "prev" });

document.getElementById("volume").oninput = (e) =>
  send("audio.set_volume", { volume: +e.target.value });
