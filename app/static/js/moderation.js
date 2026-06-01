const moderationForm = document.getElementById('moderationForm');
const moderationAction = document.getElementById('moderationAction');
const banDuration = document.getElementById('banDuration');
const moderationStatus = document.getElementById('moderationStatus');
const moderationSubmitTop = document.getElementById('moderationSubmitTop');

function setStatus(message, isError = false) {
  if (!moderationStatus) return;
  moderationStatus.textContent = message;
  moderationStatus.dataset.state = isError ? 'error' : 'success';
}

function toggleBanDuration() {
  if (!moderationAction || !banDuration) return;
  const isBan = moderationAction.value === 'ban';
  banDuration.disabled = !isBan;
  banDuration.required = isBan;
  banDuration.placeholder = isBan ? 'Ban minutes' : 'Ban minutes';
}

if (moderationAction) {
  moderationAction.addEventListener('change', toggleBanDuration);
  toggleBanDuration();
}

if (moderationSubmitTop && moderationForm) {
  moderationSubmitTop.addEventListener('click', () => {
    moderationForm.requestSubmit();
  });
}

if (moderationForm) {
  moderationForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = new FormData(moderationForm);
    const payload = Object.fromEntries(formData.entries());
    if (payload.action !== 'ban') {
      delete payload.duration_minutes;
    }

    const response = await fetch(moderationForm.action, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      setStatus(data.message || 'Unable to apply moderation action.', true);
      return;
    }

    setStatus(data.message || 'Action applied successfully.');
    moderationForm.reset();
    toggleBanDuration();
  });
}

// Auto-select room if provided in URL (?room_code=XXXX)
try {
  const params = new URLSearchParams(window.location.search);
  const pre = params.get('room_code');
  if (pre) {
    const sel = moderationForm.querySelector('[name="room_code"]');
    if (sel) sel.value = pre;
  }
} catch (err) {
  // ignore
}
