(function () {
  const display = document.getElementById('pomodoroDisplay');
  const stateLabel = document.getElementById('pomodoroState');
  const startBtn = document.getElementById('pomodoroStart');
  const pauseBtn = document.getElementById('pomodoroPause');
  const resetBtn = document.getElementById('pomodoroReset');
  const modeButtons = document.querySelectorAll('.mode-btn');

  if (!display || !stateLabel || !startBtn || !pauseBtn || !resetBtn || modeButtons.length === 0) {
    return;
  }

  const MODES = {
    study: 25 * 60,
    break: 5 * 60,
  };

  let currentMode = 'study';
  let remainingSeconds = MODES[currentMode];
  let timerId = null;

  const pad = (n) => String(n).padStart(2, '0');

  function updateDisplay(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    display.textContent = `${pad(minutes)}:${pad(secs)}`;
  }

  function updateButtonStates() {
    const running = Boolean(timerId);
    startBtn.disabled = running;
    pauseBtn.disabled = !running;
  }

  function setMode(mode) {
    currentMode = mode;
    remainingSeconds = MODES[mode];
    stateLabel.textContent = mode === 'study' ? 'Study' : 'Break';
    modeButtons.forEach((button) => {
      button.classList.toggle('active', button.dataset.mode === mode);
    });
    updateDisplay(remainingSeconds);
    updateButtonStates();
  }

  function markComplete() {
    stateLabel.textContent = currentMode === 'study' ? 'Study complete' : 'Break complete';
    display.textContent = '00:00';
    timerId = null;
    updateButtonStates();
  }

  function tick() {
    if (remainingSeconds <= 0) {
      if (timerId) {
        clearInterval(timerId);
      }
      markComplete();
      return;
    }
    remainingSeconds -= 1;
    updateDisplay(remainingSeconds);
  }

  function startTimer() {
    if (timerId) {
      return;
    }
    if (remainingSeconds <= 0) {
      remainingSeconds = MODES[currentMode];
      updateDisplay(remainingSeconds);
    }
    timerId = setInterval(tick, 1000);
    updateButtonStates();
  }

  function pauseTimer() {
    if (timerId) {
      clearInterval(timerId);
      timerId = null;
      updateButtonStates();
    }
  }

  function resetTimer() {
    pauseTimer();
    remainingSeconds = MODES[currentMode];
    stateLabel.textContent = currentMode === 'study' ? 'Study' : 'Break';
    updateDisplay(remainingSeconds);
  }

  startBtn.addEventListener('click', startTimer);
  pauseBtn.addEventListener('click', pauseTimer);
  resetBtn.addEventListener('click', resetTimer);

  modeButtons.forEach((button) => {
    button.addEventListener('click', () => {
      setMode(button.dataset.mode);
      resetTimer();
    });
  });

  setMode(currentMode);
})();
