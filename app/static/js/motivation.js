// Dashboard motivational quote widget.
// Fetches a random line from /api/quote on load and on refresh-button click.
(function () {
  const textEl = document.getElementById('quoteText');
  const refreshBtn = document.getElementById('quoteRefresh');

  if (!textEl) return;

  async function loadQuote() {
    if (refreshBtn) refreshBtn.disabled = true;
    try {
      const res = await fetch('/api/quote', {
        headers: { 'Accept': 'application/json' },
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok && data.status === 'success' && data.quote) {
        textEl.textContent = data.quote;
      } else {
        textEl.textContent = 'Keep going — you’ve got this.';
      }
    } catch (err) {
      textEl.textContent = 'Keep going — you’ve got this.';
    } finally {
      if (refreshBtn) refreshBtn.disabled = false;
    }
  }

  if (refreshBtn) {
    refreshBtn.addEventListener('click', loadQuote);
  }

  loadQuote();
})();
