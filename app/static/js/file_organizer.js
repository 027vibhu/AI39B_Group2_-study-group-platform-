document.addEventListener('DOMContentLoaded', function () {
  const addFolderBtn = document.querySelector('.folder-add-btn');
  const foldersWrapper = document.querySelector('.folders');
  const folderCountLabel = document.querySelector('.folder-count');
  const fileCountLabel = document.querySelector('.file-count');
  const previewFiles = document.querySelector('.preview-files');

  const folderFiles = {
    'Course Notes': ['Lecture 1.pdf', 'Lecture 2.pdf', 'Summary.md'],
    'Assignments': ['Assignment 1.pdf', 'Assignment 2.docx'],
    'Resources': ['Exam Tips.pdf', 'Formula Sheet.pdf']
  };

  if (!addFolderBtn || !foldersWrapper || !folderCountLabel || !fileCountLabel || !previewFiles) return;

  const updateFolderCount = () => {
    const count = foldersWrapper.querySelectorAll('.folder-item').length;
    folderCountLabel.textContent = `${count} folder${count === 1 ? '' : 's'}`;
  };

  const updateFileCount = (files = []) => {
    fileCountLabel.textContent = `${files.length} file${files.length === 1 ? '' : 's'}`;
  };

  const renderPreviewFiles = (files) => {
    previewFiles.innerHTML = '';
    if (!files || files.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'preview-empty';
      empty.textContent = 'No files available in this folder yet.';
      previewFiles.appendChild(empty);
      updateFileCount([]);
      return;
    }

    files.forEach(fileName => {
      const fileEl = document.createElement('div');
      fileEl.className = 'preview-file';
      fileEl.innerHTML = `<span>${fileName}</span><small>${fileName.split('.').pop().toUpperCase()}</small>`;
      previewFiles.appendChild(fileEl);
    });
    updateFileCount(files);
  };

  const setFolderHandlers = (folderLink) => {
    folderLink.addEventListener('click', (event) => {
      event.preventDefault();
      foldersWrapper.querySelectorAll('.folder-item').forEach(item => item.classList.remove('active'));
      folderLink.classList.add('active');

      const folderName = folderLink.textContent.trim();
      renderPreviewFiles(folderFiles[folderName] || []);
    });
  };

  const folderElements = Array.from(foldersWrapper.querySelectorAll('.folder-item'));
  folderElements.forEach(setFolderHandlers);
  updateFolderCount();
  if (folderElements.length > 0) {
    folderElements[0].click();
  } else {
    renderPreviewFiles([]);
  }

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
    renderPreviewFiles([]);
    updateFolderCount();
  });
});
