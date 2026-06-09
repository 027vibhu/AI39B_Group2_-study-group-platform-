document.addEventListener('DOMContentLoaded', () => {
  const toolItems = document.querySelectorAll('.tool-item');
  const colorSwatches = document.querySelectorAll('.color-swatch');
  const strokeButtons = document.querySelectorAll('.stroke-size');
  const canvasWrapper = document.querySelector('.whiteboard-canvas');
  const canvas = document.getElementById('whiteboardCanvas');
  const placeholder = document.querySelector('.whiteboard-placeholder');
  const clearButton = document.querySelector('.wb-btn-secondary');
  const downloadButton = document.getElementById('downloadButton');
  const inviteButton = document.querySelector('.wb-btn-primary');
  const inviteModal = document.getElementById('inviteModal');
  const inviteLinkInput = document.getElementById('inviteLinkInput');
  const copyInviteLink = document.getElementById('copyInviteLink');
  const closeInviteModal = document.getElementById('closeInviteModal');

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

  const clearCanvas = () => {
    if (!canvas || !ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    togglePlaceholder(true);
    updatePlaceholder('Board cleared. Choose a tool to begin again.');
    canvas.classList.add('board-cleared');
    setTimeout(() => canvas.classList.remove('board-cleared'), 250);
  };

  const openInviteModal = () => {
    if (!inviteModal || !inviteLinkInput) return;
    inviteModal.classList.add('open');
    inviteModal.setAttribute('aria-hidden', 'false');
    inviteLinkInput.select();
  };

  const closeInviteDialog = () => {
    if (!inviteModal) return;
    inviteModal.classList.remove('open');
    inviteModal.setAttribute('aria-hidden', 'true');
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

  const downloadBoard = () => {
    if (!canvas) return;
    const link = document.createElement('a');
    link.href = canvas.toDataURL('image/png');
    link.download = 'whiteboard.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (clearButton) {
    clearButton.addEventListener('click', clearCanvas);
  }

  if (downloadButton) {
    downloadButton.addEventListener('click', downloadBoard);
  }

  if (inviteButton) {
    inviteButton.addEventListener('click', openInviteModal);
  }

  if (closeInviteModal) {
    closeInviteModal.addEventListener('click', closeInviteDialog);
  }

  if (copyInviteLink) {
    copyInviteLink.addEventListener('click', () => {
      if (!inviteLinkInput) return;
      navigator.clipboard.writeText(inviteLinkInput.value)
        .then(() => updatePlaceholder('Invite link copied! Share it with your group.'))
        .catch(() => updatePlaceholder('Copy the invite link manually using your browser.'));
    });
  }

  if (inviteModal) {
    inviteModal.addEventListener('click', (event) => {
      if (event.target === inviteModal) {
        closeInviteDialog();
      }
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        closeInviteDialog();
      }
    });
  }
});
