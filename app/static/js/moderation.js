const moderationForm = document.getElementById('moderationForm');
const actionInput = document.getElementById('moderationAction');
const banDuration = document.getElementById('banDuration');
const banSection = document.getElementById('banDurationSection');
const moderationStatus = document.getElementById('moderationStatus');
const actionOptions = Array.from(document.querySelectorAll('.action-option'));
const presetChips = Array.from(document.querySelectorAll('.preset-chip'));
const usernameInput = document.getElementById('modUsername');
const roomSelect = document.getElementById('modRoom');
const submitBtn = document.getElementById('moderationSubmit');
const submitLabel = document.getElementById('submitLabel');

const confirmModal = document.getElementById('confirmModal');
const confirmTitle = document.getElementById('confirmTitle');
const confirmBody = document.getElementById('confirmBody');
const confirmIcon = document.getElementById('confirmIcon');
const confirmCancel = document.getElementById('confirmCancel');
const confirmApply = document.getElementById('confirmApply');
const confirmApplyLabel = document.getElementById('confirmApplyLabel');

let currentAction = 'kick';

function setStatus(message, isError = false) {
  if (!moderationStatus) return;
  moderationStatus.hidden = !message;
  moderationStatus.textContent = message || '';
  if (message) {
    moderationStatus.dataset.state = isError ? 'error' : 'success';
  } else {
    delete moderationStatus.dataset.state;
  }
}

function formatDuration(mins) {
  if (!mins || mins < 1) return '';
  if (mins % 10080 === 0) return (mins / 10080) + ' week' + (mins === 10080 ? '' : 's');
  if (mins % 1440 === 0) return (mins / 1440) + ' day' + (mins === 1440 ? '' : 's');
  if (mins % 60 === 0) return (mins / 60) + ' hour' + (mins === 60 ? '' : 's');
  return mins + ' minute' + (mins === 1 ? '' : 's');
}

function roomLabel() {
  if (!roomSelect || !roomSelect.value) return '';
  return roomSelect.options[roomSelect.selectedIndex].text;
}

function enhanceSelect(wrapper) {
  const select = wrapper.querySelector('select');
  if (!select) return;
  const iconClass = wrapper.dataset.icon || 'fa-chevron-down';

  const trigger = document.createElement('button');
  trigger.type = 'button';
  trigger.className = 'custom-select-trigger input-box input-box-select';
  trigger.setAttribute('aria-haspopup', 'listbox');
  trigger.setAttribute('aria-expanded', 'false');
  trigger.innerHTML =
    `<i class="fa-solid ${iconClass} input-icon"></i>` +
    '<span class="custom-select-value"></span>' +
    '<i class="fa-solid fa-chevron-down select-caret"></i>';
  const valueEl = trigger.querySelector('.custom-select-value');

  const menu = document.createElement('ul');
  menu.className = 'custom-select-menu';
  menu.setAttribute('role', 'listbox');

  function syncLabel() {
    const opt = select.options[select.selectedIndex];
    valueEl.textContent = opt ? opt.text : '';
    valueEl.classList.toggle('is-placeholder', !select.value);
  }

  function markSelected() {
    Array.from(menu.children).forEach((li) => {
      li.classList.toggle('is-selected', li.dataset.value === select.value);
    });
  }

  function close() {
    wrapper.dataset.open = 'false';
    trigger.setAttribute('aria-expanded', 'false');
  }

  function open() {
    wrapper.dataset.open = 'true';
    trigger.setAttribute('aria-expanded', 'true');
  }

  Array.from(select.options).forEach((opt) => {
    const li = document.createElement('li');
    li.className = 'custom-select-option';
    li.setAttribute('role', 'option');
    li.dataset.value = opt.value;
    li.textContent = opt.text;
    if (opt.value === '') li.classList.add('is-placeholder-option');
    li.addEventListener('click', () => {
      select.value = opt.value;
      select.dispatchEvent(new Event('change', { bubbles: true }));
      close();
      trigger.focus();
    });
    menu.appendChild(li);
  });

  trigger.addEventListener('click', () => {
    wrapper.dataset.open === 'true' ? close() : open();
  });

  document.addEventListener('click', (e) => {
    if (!wrapper.contains(e.target)) close();
  });

  wrapper.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      close();
      trigger.focus();
    }
  });

  select.addEventListener('change', () => {
    syncLabel();
    markSelected();
  });

  select.classList.add('custom-select-native');
  select.setAttribute('tabindex', '-1');
  wrapper.appendChild(trigger);
  wrapper.appendChild(menu);
  syncLabel();
  markSelected();
}

function selectAction(action) {
  currentAction = action === 'ban' ? 'ban' : 'kick';
  const isBan = currentAction === 'ban';
  if (actionInput) actionInput.value = currentAction;

  actionOptions.forEach((btn) => {
    const active = btn.dataset.action === currentAction;
    btn.classList.toggle('is-active', active);
    btn.setAttribute('aria-selected', String(active));
  });

  if (banSection) banSection.dataset.active = String(isBan);
  if (banDuration) {
    banDuration.required = isBan;
    if (!isBan) banDuration.value = '';
  }
  if (!isBan) presetChips.forEach((c) => c.classList.remove('is-active'));

  if (submitBtn) {
    submitBtn.classList.toggle('is-danger', isBan);
    const icon = submitBtn.querySelector('i');
    if (icon) icon.className = isBan ? 'fa-solid fa-gavel' : 'fa-solid fa-user-xmark';
  }
  if (submitLabel) submitLabel.textContent = isBan ? 'Ban member' : 'Kick member';
}

actionOptions.forEach((btn) => {
  btn.addEventListener('click', () => selectAction(btn.dataset.action));
});

presetChips.forEach((chip) => {
  chip.addEventListener('click', () => {
    if (banDuration) banDuration.value = chip.dataset.minutes;
    presetChips.forEach((c) => c.classList.toggle('is-active', c === chip));
  });
});

if (banDuration) {
  banDuration.addEventListener('input', () => {
    presetChips.forEach((c) => c.classList.toggle('is-active', c.dataset.minutes === banDuration.value));
  });
}

/* ===== Confirmation modal ===== */
function openConfirm() {
  const isBan = currentAction === 'ban';
  const name = usernameInput.value.trim();
  const room = roomLabel();

  if (confirmModal) confirmModal.dataset.action = currentAction;
  if (confirmIcon) {
    const i = confirmIcon.querySelector('i');
    if (i) i.className = isBan ? 'fa-solid fa-gavel' : 'fa-solid fa-user-xmark';
  }
  if (confirmTitle) confirmTitle.textContent = isBan ? `Ban @${name}?` : `Kick @${name}?`;

  let body;
  if (isBan) {
    const mins = parseInt(banDuration.value, 10);
    const forText = mins > 0 ? ` for ${formatDuration(mins)}` : '';
    body = `${name} will be removed from ${room} and blocked from rejoining${forText}.`;
  } else {
    body = `${name} will be removed from ${room}. They can rejoin at any time.`;
  }
  if (confirmBody) confirmBody.textContent = body;
  if (confirmApplyLabel) confirmApplyLabel.textContent = isBan ? 'Ban member' : 'Kick member';
  if (confirmApply) confirmApply.classList.toggle('is-danger', isBan);

  if (confirmModal) confirmModal.hidden = false;
}

function closeConfirm() {
  if (confirmModal) confirmModal.hidden = true;
}

async function doSubmit() {
  const formData = new FormData(moderationForm);
  const payload = Object.fromEntries(formData.entries());
  payload.action = currentAction;
  if (currentAction !== 'ban') delete payload.duration_minutes;

  try {
    const response = await fetch(moderationForm.action, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      setStatus(data.message || 'Unable to apply moderation action.', true);
      return;
    }
    setStatus(data.message || 'Action applied successfully.');
    moderationForm.reset();
    selectAction('kick');
  } catch (err) {
    setStatus('Network error — please try again.', true);
  }
}

if (moderationForm) {
  moderationForm.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!moderationForm.reportValidity()) return;
    setStatus('');
    openConfirm();
  });

  moderationForm.addEventListener('reset', () => {
    setTimeout(() => {
      selectAction('kick');
      setStatus('');
      if (roomSelect) roomSelect.dispatchEvent(new Event('change', { bubbles: true }));
    }, 0);
  });
}

if (confirmCancel) confirmCancel.addEventListener('click', closeConfirm);
if (confirmApply) {
  confirmApply.addEventListener('click', () => {
    closeConfirm();
    doSubmit();
  });
}
if (confirmModal) {
  confirmModal.addEventListener('click', (e) => {
    if (e.target === confirmModal) closeConfirm();
  });
}
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeConfirm();
});

/* ===== Audit log toggle ===== */
const auditToggle = document.getElementById('auditToggle');
const auditPanel = document.getElementById('auditPanel');
if (auditToggle && auditPanel) {
  auditToggle.addEventListener('click', () => {
    const willShow = auditPanel.hasAttribute('hidden');
    auditPanel.toggleAttribute('hidden', !willShow);
    auditToggle.setAttribute('aria-expanded', String(willShow));
    if (willShow) auditPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}

/* ===== Init ===== */
document.querySelectorAll('.custom-select').forEach(enhanceSelect);
selectAction('kick');

try {
  const params = new URLSearchParams(window.location.search);
  const pre = params.get('room_code');
  if (pre && roomSelect) {
    roomSelect.value = pre;
    roomSelect.dispatchEvent(new Event('change', { bubbles: true }));
  }
} catch (err) {
  /* ignore */
}
