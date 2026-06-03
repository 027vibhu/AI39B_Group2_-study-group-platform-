document.addEventListener('DOMContentLoaded', function () {
  const addFolderBtn = document.querySelector('.folder-add-btn');
  const foldersWrapper = document.querySelector('.folders');
  const folderCountLabel = document.querySelector('.folder-count');

  if (!addFolderBtn || !foldersWrapper || !folderCountLabel) return;

  const updateFolderCount = () => {
    const count = foldersWrapper.querySelectorAll('.folder-item').length;
    folderCountLabel.textContent = `${count} folder${count === 1 ? '' : 's'}`;
  };

  const setFolderHandlers = (folderLink) => {
    folderLink.addEventListener('click', (event) => {
      event.preventDefault();
      foldersWrapper.querySelectorAll('.folder-item').forEach(item => item.classList.remove('active'));
      folderLink.classList.add('active');
    });
  };

  foldersWrapper.querySelectorAll('.folder-item').forEach(setFolderHandlers);
  updateFolderCount();

  addFolderBtn.addEventListener('click', () => {
    const folderName = window.prompt('Enter a new folder name:');
    if (!folderName) return;

    const normalized = folderName.trim();
    if (!normalized) return;

    const duplicate = Array.from(foldersWrapper.querySelectorAll('.folder-item')).some(item =>
      item.textContent.trim().toLowerCase() === normalized.toLowerCase()
    );

    if (duplicate) {
      window.alert('That folder already exists.');
      return;
    }

    const folderLink = document.createElement('a');
    folderLink.href = '#';
    folderLink.className = 'folder-item active';
    folderLink.textContent = normalized;
    setFolderHandlers(folderLink);

    foldersWrapper.querySelectorAll('.folder-item').forEach(item => item.classList.remove('active'));
    foldersWrapper.appendChild(folderLink);
    updateFolderCount();
  });
});
