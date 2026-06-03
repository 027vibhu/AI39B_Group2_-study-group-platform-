document.addEventListener('DOMContentLoaded', function () {
  const addFolderBtn = document.querySelector('.folder-add-btn');
  const foldersWrapper = document.querySelector('.folders');

  if (!addFolderBtn || !foldersWrapper) return;

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
    folderLink.className = 'folder-item';
    folderLink.textContent = normalized;
    folderLink.addEventListener('click', (event) => event.preventDefault());

    foldersWrapper.appendChild(folderLink);
  });
});
