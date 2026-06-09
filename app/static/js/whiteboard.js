document.addEventListener('DOMContentLoaded', () => {
  const toolItems = document.querySelectorAll('.tool-item');
  const colorSwatches = document.querySelectorAll('.color-swatch');
  const strokeButtons = document.querySelectorAll('.stroke-size');
  const canvas = document.querySelector('.whiteboard-canvas');
  const placeholder = document.querySelector('.whiteboard-placeholder');
  const clearButton = document.querySelector('.wb-btn-secondary');
  const inviteButton = document.querySelector('.wb-btn-primary');

  let selectedTool = 'Pen';
  let selectedColor = '#111827';
  let selectedStroke = '2';

  const updatePlaceholder = () => {
    if (!placeholder) return;
    placeholder.textContent = `Selected tool: ${selectedTool}, color: ${selectedColor}, stroke: ${selectedStroke}px. Start drawing on the canvas.`;
  };

  const activateButtonGroup = (buttons, target) => {
    buttons.forEach((button) => button.classList.toggle('active', button === target));
  };

  toolItems.forEach((item) => {
    const setActiveTool = () => {
      selectedTool = item.textContent.trim();
      activateButtonGroup(toolItems, item);
      item.setAttribute('aria-pressed', 'true');
      updatePlaceholder();
    };

    item.addEventListener('click', setActiveTool);
    item.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        setActiveTool();
      }
    });
  });

  colorSwatches.forEach((swatch) => {
    swatch.addEventListener('click', () => {
      selectedColor = swatch.dataset.color || selectedColor;
      activateButtonGroup(colorSwatches, swatch);
      updatePlaceholder();
    });
  });

  strokeButtons.forEach((button) => {
    button.addEventListener('click', () => {
      selectedStroke = button.dataset.size || selectedStroke;
      activateButtonGroup(strokeButtons, button);
      updatePlaceholder();
    });
  });

  updatePlaceholder();

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
