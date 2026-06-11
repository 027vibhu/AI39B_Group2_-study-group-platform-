function parseDate(val) {
  // Try to parse several common formats; fallback to Date constructor
  if (!val) return null;
  // If it's already an ISO-like string, Date will handle it
  const d = new Date(val);
  return isNaN(d.getTime()) ? null : d;
}

function formatRemaining(ms) {
  if (ms <= 0) return 'Due';
  const totalSeconds = Math.floor(ms / 1000);
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  if (days > 0) return `${days}d ${hours}h ${minutes}m`;
  return `${hours}h ${minutes}m ${seconds}s`;
}

function updateCountdowns() {
  const cards = document.querySelectorAll('.exam-card');
  const now = new Date();
  cards.forEach(card => {
    const dtAttr = card.getAttribute('data-exam-datetime') || '';
    const userDate = parseDate(dtAttr);
    const timer = card.querySelector('.exam-timer');
    if (!userDate || !timer) return;
    const diff = userDate - now;
    timer.textContent = formatRemaining(diff);

    // apply urgency classes
    card.classList.remove('urgency-low', 'urgency-medium', 'urgency-high', 'expired');
    if (diff <= 0) {
      card.classList.add('expired');
    } else {
      const days = diff / (1000 * 60 * 60 * 24);
      if (days <= 7) card.classList.add('urgency-high');
      else if (days <= 30) card.classList.add('urgency-medium');
      else card.classList.add('urgency-low');
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  // If there are no server-rendered cards, try to render from window.EXAMS
  const list = document.getElementById('exam-list');
  if (list && list.children.length === 0 && Array.isArray(window.EXAMS)) {
    window.EXAMS.forEach(ex => {
      const div = document.createElement('div');
      div.className = 'exam-card';
      div.setAttribute('data-exam-datetime', ex.exam_datetime || ex.exam_datetime_str || '');
      if (ex.color) div.setAttribute('data-color', ex.color);
      div.innerHTML = `<div class="exam-title">${ex.title || 'Exam'}</div>` +
                      `<div class="exam-timer">Loading...</div>` +
                      `<div class="exam-notes">${ex.notes || ''}</div>`;
      list.appendChild(div);
    });
  }

  updateCountdowns();
  setInterval(updateCountdowns, 1000);

  // Form submission handler for creating exams
  const form = document.getElementById('create-exam-form');
  const formMessage = document.getElementById('form-message');
  if (form) {
    form.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      formMessage.textContent = '';
      const fd = new FormData(form);
      const payload = {
        title: fd.get('title'),
        exam_datetime: fd.get('exam_datetime'),
        notes: fd.get('notes'),
        color: fd.get('color') || null,
      };

      try {
        const resp = await fetch('/exams', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const data = await resp.json();
        if (resp.ok && data.status === 'success') {
          formMessage.textContent = 'Exam added.';
          // append new exam card
          const list = document.getElementById('exam-list');
          const div = document.createElement('div');
          div.className = 'exam-card';
          div.setAttribute('data-exam-datetime', payload.exam_datetime);
          if (payload.color) div.setAttribute('data-color', payload.color);
          div.innerHTML = `<div class="exam-title">${payload.title}</div>` +
                          `<div class="exam-timer">Loading...</div>` +
                          `<div class="exam-notes">${payload.notes || ''}</div>`;
          list.insertBefore(div, list.firstChild);
          form.reset();
          updateCountdowns();
        } else {
          formMessage.textContent = data.message || 'Failed to create exam.';
        }
      } catch (err) {
        formMessage.textContent = 'Network error';
      }
    });
  }
});
