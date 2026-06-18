// AI PDF summary frontend interactions
// This file handles the visual feedback for the AI summary generator.

const initNotesSummary = () => {
  const generateSummaryBtn = document.getElementById('generateSummaryBtn');
  const aiSummaryContent = document.getElementById('aiSummaryContent');
  const summaryFileInput = document.getElementById('summaryPdf');
  const summaryDropzone = document.getElementById('summaryDropzone');
  const summaryFilename = document.getElementById('summaryFilename');

  if (!generateSummaryBtn || !aiSummaryContent) {
    return;
  }

  const renderSummaryPlaceholder = (message) => {
    aiSummaryContent.innerHTML = `
      <div class="summary-placeholder">
        <h3>${message.title}</h3>
        <p>${message.body}</p>
      </div>
    `;
  };

  const renderSummaryResult = (fileName) => {
    aiSummaryContent.innerHTML = `
      <div class="summary-card">
        <div class="summary-card-header">
          <h3>Generated summary for</h3>
          <span>${fileName}</span>
        </div>
        <p class="summary-text">
          This AI-generated summary highlights the core ideas from your uploaded PDF: key concepts, main themes, and action items for efficient study.
        </p>
        <ul class="summary-bullets">
          <li>Extracts the most important topics from your notes</li>
          <li>Helps you review faster with concise insights</li>
          <li>Integrates directly into your dashboard for easy access</li>
        </ul>
      </div>
    `;
  };

  const showSelectedSummaryFile = () => {
    if (!summaryFileInput || !summaryFilename) {
      return;
    }

    if (summaryFileInput.files.length) {
      summaryFilename.textContent = summaryFileInput.files[0].name;
      summaryDropzone.classList.add('has-file');
    } else {
      summaryFilename.textContent = '';
      summaryDropzone.classList.remove('has-file');
    }
  };

  if (summaryFileInput && summaryDropzone) {
    summaryFileInput.addEventListener('change', showSelectedSummaryFile);

    ['dragenter', 'dragover'].forEach((evt) =>
      summaryDropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        summaryDropzone.classList.add('dragover');
      })
    );

    ['dragleave', 'drop'].forEach((evt) =>
      summaryDropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        summaryDropzone.classList.remove('dragover');
      })
    );

    summaryDropzone.addEventListener('drop', (e) => {
      if (e.dataTransfer.files.length) {
        summaryFileInput.files = e.dataTransfer.files;
        showSelectedSummaryFile();
      }
    });
  }

  generateSummaryBtn.addEventListener('click', () => {
    if (!summaryFileInput || !summaryFileInput.files.length) {
      renderSummaryPlaceholder({
        title: 'Upload a PDF first',
        body: 'Select a PDF in the AI summary upload box above to generate a summary.',
      });
      return;
    }

    generateSummaryBtn.disabled = true;
    generateSummaryBtn.setAttribute('aria-busy', 'true');

    renderSummaryPlaceholder({
      title: 'Generating summary...',
      body: 'Please wait while the AI analyzes your selected PDF and prepares the summary.',
    });

    const activeFile = summaryFileInput.files[0];
    setTimeout(() => {
      renderSummaryResult(activeFile.name);
      generateSummaryBtn.disabled = false;
      generateSummaryBtn.removeAttribute('aria-busy');
    }, 1200);
  });
};

window.addEventListener('DOMContentLoaded', initNotesSummary);
