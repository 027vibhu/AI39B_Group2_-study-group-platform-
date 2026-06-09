document.addEventListener('DOMContentLoaded', () => {
  const toolItems = document.querySelectorAll('.tool-item');
  const colorSwatches = document.querySelectorAll('.color-swatch');
  const strokeButtons = document.querySelectorAll('.stroke-size');
  const canvasWrapper = document.querySelector('.whiteboard-canvas');
  const canvas = document.getElementById('whiteboardCanvas');
  const placeholder = document.querySelector('.whiteboard-placeholder');
  const clearButton = document.querySelector('.wb-btn-secondary');
  const inviteButton = document.querySelector('.wb-btn-primary');

  let selectedTool = 'Pen';
  let selectedColor = '#111827';
  let selectedStroke = 2;
  let isDrawing = false;
  let lastPosition = { x: 0, y: 0 };

  const ctx = canvas ? canvas.getContext('2d') : null;

  const updatePlaceholder = (text) => {
    if (!placeholder) return;
    placeholder.textContent = text || `Selected tool: ${selectedTool}, color: ${selectedColor}, stroke: ${selectedStroke}px. Start drawing on the canvas.`;
  };

  const togglePlaceholder = (visible) => {
    if (!placeholder) return;
    placeholder.classList.toggle('hidden', !visible);
  };

  const activateButtonGroup = (buttons, target) => {
    buttons.forEach((button) => button.classList.toggle('active', button === target));
  };

  const resizeCanvas = () => {
    if (!canvas || !canvasWrapper || !ctx) return;
    const rect = canvasWrapper.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
  };

  const getPointerPosition = (event) => {
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };
  };

  const beginDrawing = (event) => {
    if (!canvas || !ctx) return;
    isDrawing = true;
    const point = getPointerPosition(event);
    lastPosition = point;
    ctx.beginPath();
    ctx.moveTo(point.x, point.y);
    ctx.lineWidth = selectedStroke;
    ctx.globalCompositeOperation = selectedTool === 'Eraser' ? 'destination-out' : 'source-over';
    const strokeColor = selectedTool === 'Eraser' ? '#000000' : selectedColor;
    ctx.strokeStyle = selectedTool === 'Highlighter' ? `${strokeColor}77` : strokeColor;
    togglePlaceholder(false);
    canvas.setPointerCapture(event.pointerId);
  };

  const drawLine = (event) => {
    if (!isDrawing || !canvas || !ctx) return;
    const point = getPointerPosition(event);
    ctx.lineTo(point.x, point.y);
    ctx.stroke();
    lastPosition = point;
  };

  const endDrawing = (event) => {
    if (!isDrawing || !canvas || !ctx) return;
    drawLine(event);
    isDrawing = false;
    if (event.pointerId) {
      canvas.releasePointerCapture(event.pointerId);
    }
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
      selectedStroke = Number(button.dataset.size) || selectedStroke;
      activateButtonGroup(strokeButtons, button);
      updatePlaceholder();
    });
  });

  if (canvas) {
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    canvas.addEventListener('pointerdown', beginDrawing);
    canvas.addEventListener('pointermove', drawLine);
    canvas.addEventListener('pointerup', endDrawing);
    canvas.addEventListener('pointerleave', endDrawing);
    canvas.addEventListener('pointercancel', endDrawing);
  }

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
