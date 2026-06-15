// ===== LOREVIA — Focus Music Player =====

// Track library (uses free, royalty-free YouTube audio IDs via embed OR direct mp3 CDN URLs)
// Using free lo-fi / ambient samples from Pixabay CDN (no API key needed, direct mp3 links)
const TRACKS = [
  // Lo-Fi
  {
    id: 1, cat: 'lofi', emoji: '☕', name: 'Coffee Shop Rain',
    url: 'https://cdn.pixabay.com/audio/2022/10/25/audio_946b5a0e9f.mp3',
  },
  {
    id: 2, cat: 'lofi', emoji: '🌙', name: 'Midnight Chill',
    url: 'https://cdn.pixabay.com/audio/2023/05/03/audio_20ec97c16e.mp3',
  },
  {
    id: 3, cat: 'lofi', emoji: '📚', name: 'Study Session',
    url: 'https://cdn.pixabay.com/audio/2022/11/22/audio_febc508520.mp3',
  },
  {
    id: 4, cat: 'lofi', emoji: '🌆', name: 'City Dusk',
    url: 'https://cdn.pixabay.com/audio/2023/03/13/audio_5c2b9a2d2f.mp3',
  },
  // Nature
  {
    id: 5, cat: 'nature', emoji: '🌧️', name: 'Gentle Rain',
    url: 'https://cdn.pixabay.com/audio/2022/03/10/audio_0625a79a6a.mp3',
  },
  {
    id: 6, cat: 'nature', emoji: '🌊', name: 'Ocean Waves',
    url: 'https://cdn.pixabay.com/audio/2021/09/06/audio_6735aed4c0.mp3',
  },
  {
    id: 7, cat: 'nature', emoji: '🌿', name: 'Forest Breeze',
    url: 'https://cdn.pixabay.com/audio/2022/01/18/audio_d0c6ff1bcc.mp3',
  },
  {
    id: 8, cat: 'nature', emoji: '🔥', name: 'Fireplace',
    url: 'https://cdn.pixabay.com/audio/2022/03/09/audio_c6ccf94451.mp3',
  },
  // Ambient
  {
    id: 9, cat: 'ambient', emoji: '🌌', name: 'Deep Space',
    url: 'https://cdn.pixabay.com/audio/2023/04/08/audio_e3fdb8e7ae.mp3',
  },
  {
    id: 10, cat: 'ambient', emoji: '🧘', name: 'Zen Garden',
    url: 'https://cdn.pixabay.com/audio/2022/10/30/audio_c8a1071bbd.mp3',
  },
  {
    id: 11, cat: 'ambient', emoji: '🏔️', name: 'Mountain Air',
    url: 'https://cdn.pixabay.com/audio/2022/09/13/audio_5ef95e9898.mp3',
  },
  {
    id: 12, cat: 'ambient', emoji: '🌅', name: 'Dawn Chorus',
    url: 'https://cdn.pixabay.com/audio/2023/01/09/audio_95dd3a7e68.mp3',
  },
  // Classical
  {
    id: 13, cat: 'classical', emoji: '🎹', name: 'Piano Nocturne',
    url: 'https://cdn.pixabay.com/audio/2021/11/13/audio_cb31a2ab87.mp3',
  },
  {
    id: 14, cat: 'classical', emoji: '🎻', name: 'String Quartet',
    url: 'https://cdn.pixabay.com/audio/2022/08/02/audio_884fe92c21.mp3',
  },
  {
    id: 15, cat: 'classical', emoji: '🎵', name: 'Soft Sonata',
    url: 'https://cdn.pixabay.com/audio/2023/02/08/audio_2c5e9bf2a9.mp3',
  },
  {
    id: 16, cat: 'classical', emoji: '🎼', name: 'Baroque Study',
    url: 'https://cdn.pixabay.com/audio/2022/12/11/audio_5daef6a64a.mp3',
  },
];

// ===== STATE =====
let currentCat  = 'lofi';
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
      <button class="track-play-btn">${globalIdx === currentIdx && isPlaying ? '⏸' : '▶'}</button>
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
  btnPlay.textContent     = isPlaying ? '⏸' : '▶';
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