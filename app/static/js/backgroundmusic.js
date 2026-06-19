// ===== LOREVIA — Focus Music Player =====

// Track library — royalty-free sources that allow direct hotlinking:
//  • Google Sound Library (actions.google.com/sounds, CC-BY 4.0) for ambient/nature
//  • SoundHelix (royalty-free instrumental) for the focus beats
// These return 200 and play directly in an <audio> element. The previous
// Pixabay CDN links 403'd because Pixabay blocks hotlinking.
const TRACKS = [
  // Rain & Storm
  {
    id: 1, cat: 'rain', emoji: '🌧️', name: 'Rain on the Roof',
    url: 'https://actions.google.com/sounds/v1/weather/rain_on_roof.ogg',
  },
  {
    id: 2, cat: 'rain', emoji: '⛈️', name: 'Heavy Rain',
    url: 'https://actions.google.com/sounds/v1/weather/rain_heavy_loud.ogg',
  },
  {
    id: 3, cat: 'rain', emoji: '🌩️', name: 'Thunderstorm',
    url: 'https://actions.google.com/sounds/v1/weather/thunderstorm.ogg',
  },
  // Nature
  {
    id: 4, cat: 'nature', emoji: '🌊', name: 'Ocean Waves',
    url: 'https://actions.google.com/sounds/v1/water/waves_crashing_on_rock_beach.ogg',
  },
  {
    id: 5, cat: 'nature', emoji: '🍃', name: 'Wind & Breeze',
    url: 'https://actions.google.com/sounds/v1/weather/wind.ogg',
  },
  // Ambient
  {
    id: 6, cat: 'ambient', emoji: '☕', name: 'Coffee Shop',
    url: 'https://actions.google.com/sounds/v1/ambiences/coffee_shop.ogg',
  },
  // Lo-Fi / Focus beats
  {
    id: 7, cat: 'lofi', emoji: '🎧', name: 'Focus Beat I',
    url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
  },
  {
    id: 8, cat: 'lofi', emoji: '🎵', name: 'Focus Beat II',
    url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3',
  },
  {
    id: 9, cat: 'lofi', emoji: '🎹', name: 'Focus Beat III',
    url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3',
  },
];

// ===== STATE =====
let currentCat  = 'rain';
let currentIdx  = null;   // index in TRACKS
let isPlaying   = false;

const audio     = document.getElementById('audioEl');
const grid      = document.getElementById('trackGrid');
const btnPlay   = document.getElementById('btnPlay');
const btnPrev   = document.getElementById('btnPrev');
const btnNext   = document.getElementById('btnNext');
const seekBar   = document.getElementById('seekBar');
const volBar    = document.getElementById('volBar');
const timeLabel = document.getElementById('timeLabel');
const playerTitle = document.getElementById('playerTitle');
const playerCat   = document.getElementById('playerCat');
const playerCover = document.getElementById('playerCover');
const playerBar   = document.getElementById('playerBar');

audio.volume = 0.7;
audio.loop   = true;

// ===== RENDER TRACKS =====
function renderTracks() {
  const filtered = TRACKS.filter(t => t.cat === currentCat);
  grid.innerHTML = '';
  filtered.forEach((track) => {
    const globalIdx = TRACKS.indexOf(track);
    const card = document.createElement('div');
    card.className = 'track-card' + (globalIdx === currentIdx ? ' active' : '');
    card.dataset.idx = globalIdx;
    card.innerHTML = `
      <span class="track-emoji">${track.emoji}</span>
      <div class="track-name">${track.name}</div>
      <div class="track-duration">${track.cat.charAt(0).toUpperCase() + track.cat.slice(1)}</div>
      <button class="track-play-btn"><span class="material-symbols-rounded">${globalIdx === currentIdx && isPlaying ? 'pause' : 'play_arrow'}</span></button>
    `;
    card.addEventListener('click', () => selectTrack(globalIdx));
    grid.appendChild(card);
  });
}

// ===== SELECT & PLAY =====
function selectTrack(idx) {
  if (currentIdx === idx) {
    togglePlay();
    return;
  }
  currentIdx = idx;
  const track = TRACKS[idx];
  audio.src = track.url;
  audio.load();
  audio.play()
    .then(() => { isPlaying = true; updateUI(); })
    .catch(() => {
      // If the CDN link fails, show a fallback message on the card
      showError(idx);
    });
}

function togglePlay() {
  if (currentIdx === null) return;
  if (isPlaying) {
    audio.pause();
    isPlaying = false;
  } else {
    audio.play();
    isPlaying = true;
  }
  updateUI();
}

// ===== PREV / NEXT =====
function prevTrack() {
  if (currentIdx === null) return;
  const cats = TRACKS.filter(t => t.cat === TRACKS[currentIdx].cat);
  const pos  = cats.indexOf(TRACKS[currentIdx]);
  const prev = cats[(pos - 1 + cats.length) % cats.length];
  selectTrack(TRACKS.indexOf(prev));
}

function nextTrack() {
  if (currentIdx === null) {
    selectTrack(0); return;
  }
  const cats = TRACKS.filter(t => t.cat === TRACKS[currentIdx].cat);
  const pos  = cats.indexOf(TRACKS[currentIdx]);
  const next = cats[(pos + 1) % cats.length];
  selectTrack(TRACKS.indexOf(next));
}

// ===== UPDATE UI =====
function updateUI() {
  // Player bar
  const track = currentIdx !== null ? TRACKS[currentIdx] : null;
  playerTitle.textContent = track ? track.name : 'No track selected';
  playerCat.textContent   = track ? track.cat.charAt(0).toUpperCase() + track.cat.slice(1) : '—';
  playerCover.textContent = track ? track.emoji : '♪';
  const playIcon = btnPlay.querySelector('.material-symbols-rounded');
  if (playIcon) playIcon.textContent = isPlaying ? 'pause' : 'play_arrow';
  if (playerBar) playerBar.classList.toggle('playing', isPlaying);
  // Re-render grid to update active states
  renderTracks();
}

function showError(idx) {
  const cards = grid.querySelectorAll('.track-card');
  cards.forEach(c => {
    if (parseInt(c.dataset.idx) === idx) {
      c.querySelector('.track-duration').textContent = 'Unable to load — try another';
    }
  });
}

// ===== SEEK =====
audio.addEventListener('timeupdate', () => {
  if (!audio.duration) return;
  const pct = (audio.currentTime / audio.duration) * 100;
  seekBar.value = pct;
  timeLabel.textContent = `${fmt(audio.currentTime)} / ${fmt(audio.duration)}`;
});

seekBar.addEventListener('input', () => {
  if (!audio.duration) return;
  audio.currentTime = (seekBar.value / 100) * audio.duration;
});

volBar.addEventListener('input', () => {
  audio.volume = volBar.value;
});

function fmt(s) {
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60).toString().padStart(2, '0');
  return `${m}:${sec}`;
}

// ===== TABS =====
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    currentCat = tab.dataset.cat;
    renderTracks();
  });
});

// ===== BUTTON LISTENERS =====
btnPlay.addEventListener('click', togglePlay);
btnPrev.addEventListener('click', prevTrack);
btnNext.addEventListener('click', nextTrack);

// ===== INIT =====
renderTracks();