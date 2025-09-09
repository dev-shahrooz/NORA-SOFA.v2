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
const volumeRange = document.getElementById("volume");
const volumeValue = document.getElementById("volume-value");
const playBtn = document.getElementById("player-play");
const pauseBtn = document.getElementById("player-pause");
const nextBtn = document.getElementById("player-next");
const prevBtn = document.getElementById("player-prev");
const trackTitle = document.getElementById("track-title");
const trackArtist = document.getElementById("track-artist");

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
function renderVolume(st) {
  const vol = st?.audio?.volume ?? 0;
  volumeRange.value = vol;
  volumeValue.textContent = vol;
}

function renderPlayer(st) {
  const p = st?.player || {};
  trackTitle.textContent = p.title || "";
  trackArtist.textContent = p.artist || "";
}

partyBtn.onclick = () => {
  send("mode.toggle");
};

btBtn.onclick = () => {
  const next = !(btStatus.textContent === "روشن");
  send("bluetooth.set", { on: next });
};

playBtn.onclick = () => send("player.play");
pauseBtn.onclick = () => send("player.pause");
nextBtn.onclick = () => send("player.next");
prevBtn.onclick = () => send("player.previous");


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
  renderReadingLight(st);
  renderBackLight(st);
  renderPartyMode(st);
  renderBluetooth(st);
  renderVolume(st);
  renderPlayer(st);

});

// Lighting apply
document.getElementById("apply-light").onclick = () => {
  const zone = document.getElementById("zone").value;
  const mode = document.getElementById("mode").value;
  const color = document.getElementById("color").value;
  const brightness = +document.getElementById("brightness").value;
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
