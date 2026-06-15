(function () {
  const card = document.getElementById('pomodoroCard');
  const dial = document.getElementById('pomodoroDial');
  const display = document.getElementById('pomodoroDisplay');
  const minutesLabel = document.getElementById('pomodoroMinutes');
  const stateLabel = document.getElementById('pomodoroState');
  const toggleBtn = document.getElementById('pomodoroToggle');
  const resetBtn = document.getElementById('pomodoroReset');
  const ring = document.getElementById('pomodoroRing');
  const segButtons = document.querySelectorAll('.seg-btn');
  const dots = document.querySelectorAll('.pomo-dot');

  // Optional: timer-settings modal (focus / break durations).
  const editBtn = document.getElementById('pomodoroEdit');
  const settingsModal = document.getElementById('pomodoroModal');
  const focusInput = document.getElementById('pomodoroFocusInput');
  const breakInput = document.getElementById('pomodoroBreakInput');
  const settingsForm = document.getElementById('pomodoroForm');
  const settingsCancel = document.getElementById('pomodoroCancelBtn');

  if (!card || !dial || !display || !minutesLabel || !stateLabel ||
      !toggleBtn || !resetBtn || !ring || segButtons.length === 0) {
    return;
  }

  const MODES = {
    study: 25 * 60,
    break: 5 * 60,
  };

  const LABELS = {
    study: 'Focus',
    break: 'Break',
  };

  // Bounds for the focus / break durations set in the settings modal (minutes).
  const MIN_MINUTES = 1;
  const MAX_MINUTES = 60;

  // Geometry: r=52 within the 120x120 viewBox.
  const RING_RADIUS = 52;
  const RING_LENGTH = 2 * Math.PI * RING_RADIUS;
  ring.style.strokeDasharray = String(RING_LENGTH);

  let currentMode = 'study';
  let remainingSeconds = MODES[currentMode];
  let timerId = null;
  let audioCtx = null;

  const pad = (n) => String(n).padStart(2, '0');

  const nextMode = (mode) => (mode === 'study' ? 'break' : 'study');

  // Lazily create/resume the audio context. Called from a user gesture (the
  // toggle click) so later interval-driven chimes are allowed to play.
  function ensureAudio() {
    try {
      if (!audioCtx) {
        const Ctx = window.AudioContext || window.webkitAudioContext;
        if (!Ctx) return;
        audioCtx = new Ctx();
      }
      if (audioCtx.state === 'suspended') audioCtx.resume();
    } catch (e) { /* audio unavailable */ }
  }

  // Short two-note chime; higher pitch entering Focus, softer entering Break.
  function playChime(mode) {
    if (!audioCtx) return;
    try {
      const now = audioCtx.currentTime;
      const base = mode === 'study' ? 880 : 587.33; // A5 vs D5
      [0, 0.16].forEach((offset, i) => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.value = base * (i === 0 ? 1 : 1.5);
        gain.gain.setValueAtTime(0.0001, now + offset);
        gain.gain.exponentialRampToValueAtTime(0.22, now + offset + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + offset + 0.34);
        osc.connect(gain).connect(audioCtx.destination);
        osc.start(now + offset);
        osc.stop(now + offset + 0.4);
      });
    } catch (e) { /* audio unavailable */ }
  }

  function setToggleIcon(playing) {
    toggleBtn.innerHTML = playing
      ? '<i class="fa-solid fa-pause"></i>'
      : '<i class="fa-solid fa-play"></i>';
    toggleBtn.setAttribute('aria-label', playing ? 'Pause timer' : 'Start timer');
  }

  // Move the progress arc to match `remainingSeconds`. While running it glides
  // over a full second (CSS transition) so the countdown looks continuous
  // rather than ticking; `instant` jumps immediately for resets/mode switches.
  function updateRing(instant) {
    const total = MODES[currentMode];
    const fraction = total > 0 ? remainingSeconds / total : 0;
    const offset = String(RING_LENGTH * (1 - fraction));
    if (instant) {
      ring.classList.add('ring-instant');
      ring.style.strokeDashoffset = offset;
      void ring.getBoundingClientRect(); // flush the jump before re-enabling glide
      ring.classList.remove('ring-instant');
    } else {
      ring.style.strokeDashoffset = offset;
    }
  }

  function updateDisplay(instant) {
    const minutes = Math.floor(remainingSeconds / 60);
    const secs = remainingSeconds % 60;
    display.textContent = `${pad(minutes)}:${pad(secs)}`;
    const totalMin = Math.round(MODES[currentMode] / 60);
    minutesLabel.textContent = `${totalMin} min`;
    updateRing(instant);
  }

  function updateDots(mode) {
    dots.forEach((dot) => {
      dot.classList.toggle('active', dot.dataset.mode === mode);
    });
  }

  function setMode(mode) {
    currentMode = mode;
    remainingSeconds = MODES[mode];
    card.dataset.mode = mode;
    stateLabel.textContent = LABELS[mode];
    segButtons.forEach((button) => {
      const active = button.dataset.mode === mode;
      button.classList.toggle('active', active);
      button.setAttribute('aria-selected', active ? 'true' : 'false');
    });
    updateDots(mode);
    updateDisplay(true);
  }

  // A session ended: chime, flip Study<->Break, and keep the loop running
  // until the user pauses or resets.
  function advanceMode() {
    const upcoming = nextMode(currentMode);
    playChime(upcoming);
    setMode(upcoming);
  }

  function tick() {
    if (remainingSeconds <= 1) {
      advanceMode();
      return;
    }
    remainingSeconds -= 1;
    updateDisplay();
  }

  function startTimer() {
    if (timerId) return;
    if (remainingSeconds <= 0) {
      remainingSeconds = MODES[currentMode];
      stateLabel.textContent = LABELS[currentMode];
    }
    timerId = setInterval(tick, 1000);
    setToggleIcon(true);
  }

  function pauseTimer() {
    if (timerId) {
      clearInterval(timerId);
      timerId = null;
    }
    setToggleIcon(false);
    updateRing(true); // freeze the arc instead of letting it glide past
  }

  function resetTimer() {
    pauseTimer();
    remainingSeconds = MODES[currentMode];
    stateLabel.textContent = LABELS[currentMode];
    updateDisplay(true);
  }

  toggleBtn.addEventListener('click', () => {
    ensureAudio();
    if (timerId) {
      pauseTimer();
    } else {
      startTimer();
    }
  });

  resetBtn.addEventListener('click', resetTimer);

  segButtons.forEach((button) => {
    button.addEventListener('click', () => {
      pauseTimer();
      setMode(button.dataset.mode);
    });
  });

  // ----- Timer-settings modal (focus / break durations) -----

  const clampMinutes = (value) => {
    const n = Math.round(Number(value));
    if (!Number.isFinite(n)) return null;
    return Math.min(Math.max(n, MIN_MINUTES), MAX_MINUTES);
  };

  function openSettings() {
    if (!settingsModal) return;
    focusInput.value = Math.round(MODES.study / 60);
    breakInput.value = Math.round(MODES.break / 60);
    settingsModal.classList.add('open');
    settingsModal.setAttribute('aria-hidden', 'false');
    focusInput.focus();
  }

  function closeSettings() {
    if (!settingsModal) return;
    settingsModal.classList.remove('open');
    settingsModal.setAttribute('aria-hidden', 'true');
  }

  if (editBtn && settingsModal && settingsForm) {
    editBtn.addEventListener('click', openSettings);
    if (settingsCancel) settingsCancel.addEventListener('click', closeSettings);

    settingsForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const focus = clampMinutes(focusInput.value);
      const brk = clampMinutes(breakInput.value);
      if (focus) MODES.study = focus * 60;
      if (brk) MODES.break = brk * 60;

      // Apply to the live timer: stop, refill the current mode, repaint.
      pauseTimer();
      remainingSeconds = MODES[currentMode];
      stateLabel.textContent = LABELS[currentMode];
      updateDisplay(true);
      closeSettings();
    });
  }

  setMode(currentMode);
  setToggleIcon(false);
})();
