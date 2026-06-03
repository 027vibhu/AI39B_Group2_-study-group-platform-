document.addEventListener('DOMContentLoaded', function () {
  const addFolderBtn = document.querySelector('.folder-add-btn');
  const foldersWrapper = document.querySelector('.folders');
  const folderCountLabel = document.querySelector('.folder-count');
  const fileCountLabel = document.querySelector('.file-count');
  const previewFiles = document.querySelector('.preview-files');
  const addFileBtn = document.querySelector('.preview-add-file-btn');
  const folderSearch = document.querySelector('.folder-search');
  const folderNoResults = document.querySelector('.folder-no-results');

  const folderFiles = {
    'Course Notes': ['Lecture 1.pdf', 'Lecture 2.pdf', 'Summary.md'],
    'Assignments': ['Assignment 1.pdf', 'Assignment 2.docx'],
    'Resources': ['Exam Tips.pdf', 'Formula Sheet.pdf']
  };

  if (!addFolderBtn || !foldersWrapper || !folderCountLabel || !fileCountLabel || !previewFiles || !addFileBtn || !folderSearch || !folderNoResults) return;

  const updateFolderCount = () => {
    const count = foldersWrapper.querySelectorAll('.folder-item').length;
    folderCountLabel.textContent = `${count} folder${count === 1 ? '' : 's'}`;
  };

  const updateFileCount = (files = []) => {
    fileCountLabel.textContent = `${files.length} file${files.length === 1 ? '' : 's'}`;
  };

  const renderPreviewFiles = (folderName, files) => {
    previewFiles.innerHTML = '';
    if (!folderName) {
      const empty = document.createElement('div');
      empty.className = 'preview-empty';
      empty.textContent = 'Select a folder to preview files.';
      previewFiles.appendChild(empty);
      addFileBtn.disabled = true;
      updateFileCount([]);
      return;
    }

    addFileBtn.disabled = false;

    if (!files || files.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'preview-empty';
      empty.textContent = 'No files available in this folder yet.';
      previewFiles.appendChild(empty);
      updateFileCount([]);
      return;
    }

    files.forEach((fileName, index) => {
      const fileEl = document.createElement('div');
      fileEl.className = 'preview-file';
      fileEl.innerHTML = `
        <div>
          <span>${fileName}</span>
          <small>${fileName.split('.').pop().toUpperCase()}</small>
        </div>
        <button class="preview-remove-file-btn" type="button" aria-label="Remove file">✕</button>
      `;

      const removeBtn = fileEl.querySelector('.preview-remove-file-btn');
      removeBtn.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        const activeFolder = currentFolderName;
        if (!activeFolder) return;
        folderFiles[activeFolder] = folderFiles[activeFolder] || [];
        folderFiles[activeFolder].splice(index, 1);

        const activeFolderLink = foldersWrapper.querySelector('.folder-item.active');
        if (activeFolderLink) {
          updateBadge(activeFolderLink, folderFiles[activeFolder]);
        }

        renderPreviewFiles(activeFolder, folderFiles[activeFolder]);
      });

      previewFiles.appendChild(fileEl);
    });
    updateFileCount(files);
  };

  const updateBadge = (folderLink, files) => {
    let badge = folderLink.querySelector('.folder-badge');
    if (!badge) {
      badge = document.createElement('span');
      badge.className = 'folder-badge';
      folderLink.appendChild(badge);
    }
    badge.textContent = files.length;
  };

  const getFolderName = (folderLink) => folderLink.dataset.folderName || folderLink.textContent.trim();

  let currentFolderName = null;

  const removeFolder = (folderLink) => {
    const folderName = getFolderName(folderLink);
    if (currentFolderName === folderName) {
      currentFolderName = null;
      renderPreviewFiles(null, []);
    }

    delete folderFiles[folderName];
    folderLink.remove();
    updateFolderCount();
    updateSearchResults();
  };

  const setFolderHandlers = (folderLink) => {
    const removeBtn = folderLink.querySelector('.folder-remove-btn');
    if (removeBtn) {
      removeBtn.addEventListener('click', (event) => {
        event.stopPropagation();
        event.preventDefault();
        removeFolder(folderLink);
      });
    }

    folderLink.addEventListener('click', (event) => {
      event.preventDefault();
      foldersWrapper.querySelectorAll('.folder-item').forEach(item => item.classList.remove('active'));
      folderLink.classList.add('active');

      currentFolderName = getFolderName(folderLink);
      renderPreviewFiles(currentFolderName, folderFiles[currentFolderName] || []);
    });
  };

  const folderElements = Array.from(foldersWrapper.querySelectorAll('.folder-item'));
  folderElements.forEach(folderLink => {
    const name = getFolderName(folderLink);
    updateBadge(folderLink, folderFiles[name] || []);
    setFolderHandlers(folderLink);
  });

  updateFolderCount();
  if (folderElements.length > 0) {
    folderElements[0].click();
  } else {
    renderPreviewFiles(null, []);
  }

  const updateSearchResults = () => {
    const query = folderSearch.value.trim().toLowerCase();
    let visible = 0;
    let firstVisible = null;

    foldersWrapper.querySelectorAll('.folder-item').forEach(item => {
      const label = item.dataset.folderName?.toLowerCase() || item.textContent.trim().toLowerCase();
      const matches = label.includes(query);
      item.style.display = matches ? '' : 'none';
      if (matches) {
        visible += 1;
        if (!firstVisible) firstVisible = item;
      }
    });

    folderNoResults.classList.toggle('hidden', visible > 0);

    const activeItem = foldersWrapper.querySelector('.folder-item.active');
    if (activeItem && activeItem.style.display === 'none') {
      if (firstVisible) {
        firstVisible.click();
      } else {
        currentFolderName = null;
        renderPreviewFiles(null, []);
      }
    }
  };

  folderSearch.addEventListener('input', updateSearchResults);

  addFolderBtn.addEventListener('click', () => {
    const folderName = window.prompt('Enter a new folder name:');
    if (!folderName) return;

    const normalized = folderName.trim();
    if (!normalized) return;

    const duplicate = Array.from(foldersWrapper.querySelectorAll('.folder-item')).some(item =>
      (item.dataset.folderName || item.textContent.trim()).toLowerCase() === normalized.toLowerCase()
    );

    if (duplicate) {
      window.alert('That folder already exists.');
      return;
    }

    const folderLink = document.createElement('a');
    folderLink.href = '#';
    folderLink.className = 'folder-item active';
    folderLink.dataset.folderName = normalized;
    folderLink.innerHTML = `<span class="folder-item-label">${normalized}</span><span class="folder-badge">0</span><button class="folder-remove-btn" type="button" aria-label="Remove folder">×</button>`;
    setFolderHandlers(folderLink);

    foldersWrapper.querySelectorAll('.folder-item').forEach(item => item.classList.remove('active'));
    foldersWrapper.appendChild(folderLink);
    currentFolderName = normalized;
    renderPreviewFiles(currentFolderName, []);
    updateFolderCount();
    folderSearch.value = '';
    updateSearchResults();
  });

  addFileBtn.addEventListener('click', () => {
    if (!currentFolderName) return;

    const fileName = window.prompt('Enter a file name:');
    if (!fileName) return;

    const normalizedName = fileName.trim();
    if (!normalizedName) return;

    folderFiles[currentFolderName] = folderFiles[currentFolderName] || [];
    folderFiles[currentFolderName].push(normalizedName);

    const activeFolder = foldersWrapper.querySelector('.folder-item.active');
    if (activeFolder) {
      updateBadge(activeFolder, folderFiles[currentFolderName]);
    }
    renderPreviewFiles(currentFolderName, folderFiles[currentFolderName]);
  });
});
