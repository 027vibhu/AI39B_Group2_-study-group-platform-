document.addEventListener('DOMContentLoaded', () => {
  const toolItems = document.querySelectorAll('.tool-item');
  const canvas = document.querySelector('.whiteboard-canvas');
  const placeholder = document.querySelector('.whiteboard-placeholder');
  const clearButton = document.querySelector('.wb-btn-secondary');
  const inviteButton = document.querySelector('.wb-btn-primary');

  toolItems.forEach((item) => {
    const setActive = () => {
      toolItems.forEach((tool) => {
        tool.classList.remove('active');
        tool.setAttribute('aria-pressed', 'false');
      });
      item.classList.add('active');
      item.setAttribute('aria-pressed', 'true');
      if (placeholder) {
        placeholder.textContent = `Selected tool: ${item.textContent.trim()}. Start drawing on the canvas.`;
      }
    };

    item.addEventListener('click', setActive);
    item.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        setActive();
      }
    });
  });

  if (clearButton) {
    clearButton.addEventListener('click', () => {
      if (placeholder) {
        placeholder.textContent = 'Board cleared. Choose a tool to begin again.';
      }
      canvas.classList.add('board-cleared');
      setTimeout(() => canvas.classList.remove('board-cleared'), 250);
    });
  }

  if (inviteButton) {
    inviteButton.addEventListener('click', () => {
      window.alert('Invite link copied to clipboard! Share it with your group.');
    });
  }
});
