document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.querySelector('.search-box input');
  const userRows = Array.from(document.querySelectorAll('.user-row'));
  const filterButtons = Array.from(document.querySelectorAll('.filter-group button'));
  const modalBackdrop = document.querySelector('.modal-backdrop');
  const cancelButton = modalBackdrop.querySelector('.btn.btn-secondary');
  const confirmButton = modalBackdrop.querySelector('.btn.btn-danger');
  let activeAction = null;

  function updateFilter(filter) {
    userRows.forEach(row => {
      const status = row.querySelector('.user-status')?.textContent?.trim().toLowerCase();
      const matchesStatus = filter === 'all' || status === filter;
      const matchesSearch = row.textContent.toLowerCase().includes(searchInput.value.toLowerCase());
      row.style.display = matchesStatus && matchesSearch ? '' : 'none';
    });
  }

  function setActiveFilter(button) {
    filterButtons.forEach(btn => btn.classList.toggle('active', btn === button));
    const filter = button.textContent.trim().toLowerCase();
    updateFilter(filter === 'all' ? 'all' : filter);
  }

  filterButtons.forEach(button => {
    button.addEventListener('click', () => setActiveFilter(button));
  });

  const searchButton = document.querySelector('.search-box button');

  function refreshCurrentFilter() {
    const activeButton = document.querySelector('.filter-group .active');
    const filter = activeButton ? activeButton.textContent.trim().toLowerCase() : 'all';
    updateFilter(filter === 'all' ? 'all' : filter);
  }

  searchInput.addEventListener('input', refreshCurrentFilter);
  searchButton?.addEventListener('click', refreshCurrentFilter);

  document.querySelectorAll('.action-btn').forEach(button => {
    button.addEventListener('click', () => {
      activeAction = button.textContent.trim();
      modalBackdrop.hidden = false;
      modalBackdrop.querySelector('h2').textContent = 'Confirm Action';
      modalBackdrop.querySelector('p').textContent = `Are you sure you want to ${activeAction.toLowerCase()} this user?`;
    });
  });

  cancelButton.addEventListener('click', () => {
    modalBackdrop.hidden = true;
    activeAction = null;
  });

  confirmButton.addEventListener('click', () => {
    modalBackdrop.hidden = true;
    activeAction = null;
  });

  modalBackdrop.addEventListener('click', event => {
    if (event.target === modalBackdrop) {
      modalBackdrop.hidden = true;
      activeAction = null;
    }
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !modalBackdrop.hidden) {
      modalBackdrop.hidden = true;
      activeAction = null;
    }
  });
});
