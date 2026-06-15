document.addEventListener('DOMContentLoaded', () => {
  // --- Element refs ------------------------------------------------------
  const toolButtons = document.querySelectorAll('.wb-tool[data-tool]');
  const colorSwatches = document.querySelectorAll('.color-swatch');
  const customColorInput = document.getElementById('customColor');
  const strokeRange = document.getElementById('strokeRange');
  const strokeValue = document.getElementById('strokeValue');

  const shapesToolBtn = document.getElementById('shapesToolBtn');
  const shapesFlyout = document.getElementById('shapesFlyout');
  const shapeOptions = document.querySelectorAll('.wb-shape-opt[data-shape]');

  const canvasWrapper = document.getElementById('canvasWrapper');
  const canvas = document.getElementById('whiteboardCanvas');
  const placeholder = document.querySelector('.whiteboard-placeholder');
  const toolbarStatus = document.getElementById('toolbarStatus');
  const statusHint = document.getElementById('statusHint');

  const clearButton = document.getElementById('clearButton');
  const downloadButton = document.getElementById('downloadButton');
  const inviteButton = document.getElementById('inviteButton');
  const inviteModal = document.getElementById('inviteModal');
  const inviteLinkInput = document.getElementById('inviteLinkInput');
  const copyInviteLink = document.getElementById('copyInviteLink');
  const closeInviteModal = document.getElementById('closeInviteModal');
  const participantList = document.getElementById('participantList');
  const participantCount = document.getElementById('participantCount');

  const config = window.WHITEBOARD || {};
  const boardCode = config.code || '';
  const displayName = config.username || 'Guest';

  // --- State -------------------------------------------------------------
  let selectedTool = 'Pen';
  let selectedShape = 'rectangle';
  let selectedColor = '#111827';
  let selectedStroke = 3;
  let isDrawing = false;
  let lastPosition = { x: 0, y: 0 };
  let initialCanvasData = null; // snapshot for live shape preview
  let currentPoints = [];

  const TOOL_ICONS = {
    Pen: 'fa-pen',
    Highlighter: 'fa-highlighter',
    Eraser: 'fa-eraser',
    Text: 'fa-font',
    Shapes: 'fa-shapes',
  };

  const ctx = canvas ? canvas.getContext('2d') : null;

  // --- Socket.IO collaboration -------------------------------------------
  const socket = (boardCode && typeof io === 'function') ? io() : null;
  let saveTimer = null;

  const scheduleStateSave = () => {
    if (!socket || !canvas) return;
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => {
      socket.emit('whiteboard_save_state', {
        board: boardCode,
        username: displayName,
        state: canvas.toDataURL('image/png'),
      });
    }, 800);
  };

  const emitAction = (action, payload) => {
    if (!socket) return;
    socket.emit('whiteboard_action', {
      board: boardCode,
      username: displayName,
      action,
      payload,
    });
    scheduleStateSave();
  };

  // --- UI helpers --------------------------------------------------------
  const togglePlaceholder = (visible) => {
    if (!placeholder) return;
    placeholder.classList.toggle('hidden', !visible);
  };

  const updateStatus = (hint) => {
    if (toolbarStatus) {
      const icon = TOOL_ICONS[selectedTool] || 'fa-pen';
      const label = selectedTool === 'Shapes' ? `Shapes (${selectedShape})` : selectedTool;
      toolbarStatus.innerHTML =
        `<i class="fa-solid ${icon}"></i> ${label} • ${selectedColor} • ${selectedStroke}px`;
    }
    if (hint && statusHint) statusHint.textContent = hint;
  };

  const activateButtonGroup = (buttons, target) => {
    buttons.forEach((b) => {
      const on = b === target;
      b.classList.toggle('active', on);
      if (b.hasAttribute('aria-pressed')) b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  };

  const setShapesFlyout = (open) => {
    if (!shapesFlyout) return;
    shapesFlyout.classList.toggle('open', open);
  };

  // --- Canvas sizing -----------------------------------------------------
  const resizeCanvas = () => {
    if (!canvas || !canvasWrapper || !ctx) return;
    const snapshot = canvas.width && canvas.height ? canvas.toDataURL('image/png') : null;
    const rect = canvasWrapper.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.max(1, Math.round(rect.width * dpr));
    canvas.height = Math.max(1, Math.round(rect.height * dpr));
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    if (snapshot) {
      const img = new Image();
      img.onload = () => ctx.drawImage(img, 0, 0, rect.width, rect.height);
      img.src = snapshot;
    }
  };

  const getPointerPosition = (event) => {
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };
  };

  // --- Rendering primitives (shared by local + remote actions) -----------
  const applyStrokeStyle = (tool, color, stroke) => {
    ctx.lineWidth = stroke;
    ctx.globalCompositeOperation = tool === 'Eraser' ? 'destination-out' : 'source-over';
    const strokeColor = tool === 'Eraser' ? '#000000' : color;
    ctx.strokeStyle = tool === 'Highlighter' ? `${strokeColor}66` : strokeColor;
    ctx.fillStyle = tool === 'Highlighter' ? `${strokeColor}44` : strokeColor;
  };

  const renderStroke = ({ tool, color, stroke, points }) => {
    if (!ctx || !points || points.length === 0) return;
    ctx.save();
    applyStrokeStyle(tool, color, stroke);
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i += 1) {
      ctx.lineTo(points[i].x, points[i].y);
    }
    if (points.length === 1) {
      ctx.lineTo(points[0].x + 0.01, points[0].y + 0.01);
    }
    ctx.stroke();
    ctx.restore();
    togglePlaceholder(false);
  };

  // Draw a shape given its bounding box (x,y -> x+width,y+height).
  const drawShapePath = (shape, x, y, width, height, color, stroke) => {
    ctx.save();
    ctx.globalCompositeOperation = 'source-over';
    ctx.strokeStyle = color;
    ctx.lineWidth = stroke;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.beginPath();

    if (shape === 'ellipse') {
      const cx = x + width / 2;
      const cy = y + height / 2;
      ctx.ellipse(cx, cy, Math.abs(width / 2), Math.abs(height / 2), 0, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(79, 70, 229, 0.10)';
      ctx.fill();
      ctx.stroke();
    } else if (shape === 'line' || shape === 'arrow') {
      const x2 = x + width;
      const y2 = y + height;
      ctx.moveTo(x, y);
      ctx.lineTo(x2, y2);
      ctx.stroke();
      if (shape === 'arrow') {
        const angle = Math.atan2(y2 - y, x2 - x);
        const head = Math.max(10, stroke * 3);
        ctx.beginPath();
        ctx.moveTo(x2, y2);
        ctx.lineTo(x2 - head * Math.cos(angle - Math.PI / 6), y2 - head * Math.sin(angle - Math.PI / 6));
        ctx.moveTo(x2, y2);
        ctx.lineTo(x2 - head * Math.cos(angle + Math.PI / 6), y2 - head * Math.sin(angle + Math.PI / 6));
        ctx.stroke();
      }
    } else {
      // rectangle (default)
      ctx.rect(x, y, width, height);
      ctx.fillStyle = 'rgba(79, 70, 229, 0.10)';
      ctx.fill();
      ctx.stroke();
    }
    ctx.restore();
  };

  const renderShape = (payload) => {
    if (!ctx) return;
    const shape = payload.shape || 'rectangle';
    drawShapePath(shape, payload.x, payload.y, payload.width, payload.height, payload.color, payload.stroke);
    togglePlaceholder(false);
  };

  const renderText = ({ text, x, y, color, size }) => {
    if (!ctx) return;
    ctx.save();
    ctx.globalCompositeOperation = 'source-over';
    ctx.fillStyle = color;
    ctx.textBaseline = 'top';
    ctx.font = `${size}px Arial, sans-serif`;
    String(text).split('\n').forEach((line, i) => {
      ctx.fillText(line, x, y + i * size * 1.15);
    });
    ctx.restore();
    togglePlaceholder(false);
  };

  const applyRemoteAction = (action, payload) => {
    if (!payload) return;
    if (action === 'stroke') renderStroke(payload);
    else if (action === 'shape') renderShape(payload);
    else if (action === 'text') renderText(payload);
  };

  const clearCanvas = (local = true) => {
    if (!canvas || !ctx) return;
    removeTextEditor();
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.restore();
    togglePlaceholder(true);
    if (canvasWrapper) {
      canvasWrapper.classList.add('board-cleared');
      setTimeout(() => canvasWrapper.classList.remove('board-cleared'), 250);
    }
    if (local && socket) {
      socket.emit('whiteboard_clear', { board: boardCode, username: displayName });
    }
  };

  // --- Inline text editor ------------------------------------------------
  let textEditor = null;

  const removeTextEditor = () => {
    if (textEditor && textEditor.parentNode) {
      textEditor.parentNode.removeChild(textEditor);
    }
    textEditor = null;
  };

  const commitTextEditor = () => {
    if (!textEditor) return;
    const text = textEditor.value.trim();
    const x = parseFloat(textEditor.dataset.x);
    const y = parseFloat(textEditor.dataset.y);
    const size = parseFloat(textEditor.dataset.size);
    const color = textEditor.dataset.color;
    removeTextEditor();
    if (!text) return;
    const payload = { text, x, y, color, size };
    renderText(payload);
    emitAction('text', payload);
  };

  const openTextEditor = (point) => {
    removeTextEditor();
    const size = Math.max(14, selectedStroke * 5);
    textEditor = document.createElement('textarea');
    textEditor.className = 'wb-text-input';
    textEditor.rows = 1;
    textEditor.style.left = `${point.x}px`;
    textEditor.style.top = `${point.y}px`;
    textEditor.style.color = selectedColor;
    textEditor.style.fontSize = `${size}px`;
    textEditor.dataset.x = point.x;
    // canvas baseline is "top" so align the editor's text box to the same y.
    textEditor.dataset.y = point.y;
    textEditor.dataset.size = size;
    textEditor.dataset.color = selectedColor;

    textEditor.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        commitTextEditor();
      } else if (e.key === 'Escape') {
        e.preventDefault();
        removeTextEditor();
      }
    });
    textEditor.addEventListener('blur', commitTextEditor);
    // Auto-grow with content.
    textEditor.addEventListener('input', () => {
      textEditor.style.height = 'auto';
      textEditor.style.height = `${textEditor.scrollHeight}px`;
    });

    canvasWrapper.appendChild(textEditor);
    togglePlaceholder(false);
    setTimeout(() => textEditor && textEditor.focus(), 0);
  };

  // --- Local drawing -----------------------------------------------------
  const beginDrawing = (event) => {
    if (!canvas || !ctx) return;
    if (event.button !== undefined && event.button !== 0) return; // left button only
    const point = getPointerPosition(event);

    if (selectedTool === 'Text') {
      openTextEditor(point);
      return;
    }

    isDrawing = true;
    lastPosition = point;
    currentPoints = [point];
    ctx.beginPath();
    applyStrokeStyle(selectedTool, selectedColor, selectedStroke);

    if (selectedTool === 'Shapes') {
      // Snapshot so we can repaint the preview on every move.
      initialCanvasData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    } else {
      ctx.moveTo(point.x, point.y);
      // Render the initial dot so a single click leaves a mark.
      renderStroke({ tool: selectedTool, color: selectedColor, stroke: selectedStroke, points: [point] });
    }

    togglePlaceholder(false);
    try { canvas.setPointerCapture(event.pointerId); } catch (e) { /* ignore */ }
  };

  const drawMove = (event) => {
    if (!isDrawing || !canvas || !ctx) return;
    const point = getPointerPosition(event);

    if (selectedTool === 'Shapes') {
      if (initialCanvasData) ctx.putImageData(initialCanvasData, 0, 0);
      drawShapePath(
        selectedShape,
        lastPosition.x, lastPosition.y,
        point.x - lastPosition.x, point.y - lastPosition.y,
        selectedColor, selectedStroke
      );
      return;
    }

    // Draw segment-by-segment (not one growing path) so a semi-transparent
    // highlighter doesn't darken where the live path overlaps itself.
    applyStrokeStyle(selectedTool, selectedColor, selectedStroke);
    ctx.beginPath();
    ctx.moveTo(lastPosition.x, lastPosition.y);
    ctx.lineTo(point.x, point.y);
    ctx.stroke();
    lastPosition = point;
    currentPoints.push(point);
  };

  const endDrawing = (event) => {
    if (!isDrawing || !canvas || !ctx) return;
    const point = getPointerPosition(event);

    if (selectedTool === 'Shapes') {
      if (initialCanvasData) ctx.putImageData(initialCanvasData, 0, 0);
      const payload = {
        shape: selectedShape,
        color: selectedColor,
        stroke: selectedStroke,
        x: lastPosition.x,
        y: lastPosition.y,
        width: point.x - lastPosition.x,
        height: point.y - lastPosition.y,
      };
      renderShape(payload);
      emitAction('shape', payload);
      initialCanvasData = null;
    } else {
      emitAction('stroke', {
        tool: selectedTool,
        color: selectedColor,
        stroke: selectedStroke,
        points: currentPoints,
      });
    }

    isDrawing = false;
    currentPoints = [];
    if (event.pointerId !== undefined) {
      try { canvas.releasePointerCapture(event.pointerId); } catch (e) { /* ignore */ }
    }
  };

  // --- Tool / shape / color / stroke selection ---------------------------
  toolButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      selectedTool = btn.dataset.tool;
      activateButtonGroup(toolButtons, btn);

      // The shapes flyout only matters when Shapes is the active tool.
      setShapesFlyout(selectedTool === 'Shapes');

      const hints = {
        Pen: 'Drag to draw freehand',
        Highlighter: 'Drag to highlight (semi-transparent)',
        Eraser: 'Drag over strokes to erase them',
        Text: 'Click on the canvas, then type. Enter to place, Esc to cancel',
        Shapes: 'Pick a shape, then drag to size it',
      };
      updateStatus(hints[selectedTool] || 'Drag on the canvas to draw');
    });
  });

  shapeOptions.forEach((opt) => {
    opt.addEventListener('click', () => {
      selectedShape = opt.dataset.shape || 'rectangle';
      activateButtonGroup(shapeOptions, opt);
      // Selecting a shape implies the Shapes tool.
      const shapesBtn = document.querySelector('.wb-tool[data-tool="Shapes"]');
      if (shapesBtn) {
        selectedTool = 'Shapes';
        activateButtonGroup(toolButtons, shapesBtn);
      }
      updateStatus(`Drag to draw a ${selectedShape}`);
    });
  });

  // Toggle the flyout when clicking the Shapes tool button directly.
  if (shapesToolBtn) {
    shapesToolBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      setShapesFlyout(!shapesFlyout.classList.contains('open'));
    });
  }
  document.addEventListener('click', (e) => {
    if (shapesFlyout && !shapesFlyout.contains(e.target) && e.target !== shapesToolBtn
        && !shapesToolBtn.contains(e.target)) {
      setShapesFlyout(false);
    }
  });

  colorSwatches.forEach((swatch) => {
    swatch.addEventListener('click', () => {
      selectedColor = swatch.dataset.color || selectedColor;
      activateButtonGroup(colorSwatches, swatch);
      updateStatus();
    });
  });

  if (customColorInput) {
    customColorInput.addEventListener('input', () => {
      selectedColor = customColorInput.value;
      colorSwatches.forEach((s) => s.classList.remove('active'));
      updateStatus();
    });
  }

  if (strokeRange) {
    strokeRange.addEventListener('input', () => {
      selectedStroke = Number(strokeRange.value) || selectedStroke;
      if (strokeValue) strokeValue.textContent = `${selectedStroke} px`;
      updateStatus();
    });
  }

  // --- Canvas events -----------------------------------------------------
  if (canvas) {
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    canvas.addEventListener('pointerdown', beginDrawing);
    canvas.addEventListener('pointermove', drawMove);
    canvas.addEventListener('pointerup', endDrawing);
    canvas.addEventListener('pointerleave', endDrawing);
    canvas.addEventListener('pointercancel', endDrawing);
  }

  updateStatus('Drag on the canvas to draw');

  // --- Toolbar buttons ---------------------------------------------------
  const downloadBoard = () => {
    if (!canvas) return;
    // Flatten onto white so the exported PNG isn't transparent.
    const exportCanvas = document.createElement('canvas');
    exportCanvas.width = canvas.width;
    exportCanvas.height = canvas.height;
    const ex = exportCanvas.getContext('2d');
    ex.fillStyle = '#ffffff';
    ex.fillRect(0, 0, exportCanvas.width, exportCanvas.height);
    ex.drawImage(canvas, 0, 0);
    const link = document.createElement('a');
    link.href = exportCanvas.toDataURL('image/png');
    link.download = `whiteboard-${boardCode || 'board'}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (clearButton) clearButton.addEventListener('click', () => clearCanvas(true));
  if (downloadButton) downloadButton.addEventListener('click', downloadBoard);

  // --- Invite modal ------------------------------------------------------
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

  if (inviteButton) inviteButton.addEventListener('click', openInviteModal);
  if (closeInviteModal) closeInviteModal.addEventListener('click', closeInviteDialog);
  if (copyInviteLink) {
    copyInviteLink.addEventListener('click', () => {
      if (!inviteLinkInput) return;
      navigator.clipboard.writeText(inviteLinkInput.value)
        .then(() => { copyInviteLink.innerHTML = '<i class="fa-solid fa-check"></i> Copied'; })
        .catch(() => { copyInviteLink.innerHTML = '<i class="fa-solid fa-copy"></i> Copy manually'; });
      setTimeout(() => { copyInviteLink.innerHTML = '<i class="fa-solid fa-copy"></i> Copy'; }, 1800);
    });
  }
  if (inviteModal) {
    inviteModal.addEventListener('click', (event) => {
      if (event.target === inviteModal) closeInviteDialog();
    });
  }
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeInviteDialog();
  });

  // --- Participants panel ------------------------------------------------
  const renderParticipants = (participants) => {
    const names = participants && participants.length ? participants : [displayName];
    if (participantCount) participantCount.textContent = names.length;
    if (!participantList) return;
    participantList.innerHTML = '';
    names.forEach((name) => {
      const initials = name.slice(0, 2).toUpperCase();
      const li = document.createElement('li');
      li.className = 'collaborator';
      li.innerHTML = `
        <span class="avatar">${initials}</span>
        <div>
          <span class="collab-name">${name}${name === displayName ? ' (you)' : ''}</span>
          <span class="collab-status">Online</span>
        </div>`;
      participantList.appendChild(li);
    });
  };
  renderParticipants([displayName]);

  // --- Socket wiring -----------------------------------------------------
  if (socket) {
    socket.on('connect', () => {
      socket.emit('join_whiteboard', { board: boardCode, username: displayName });
      socket.emit('whiteboard_request_state', { board: boardCode });
    });

    socket.on('whiteboard_action', (data) => {
      if (!data || data.code !== boardCode) return;
      applyRemoteAction(data.action, data.payload);
    });

    socket.on('whiteboard_state', (data) => {
      if (!data || data.code !== boardCode || !data.state) return;
      const img = new Image();
      img.onload = () => {
        const rect = canvasWrapper.getBoundingClientRect();
        ctx.drawImage(img, 0, 0, rect.width, rect.height);
        togglePlaceholder(false);
      };
      img.src = data.state;
    });

    socket.on('whiteboard_cleared', (data) => {
      if (!data || data.code !== boardCode) return;
      clearCanvas(false);
    });

    socket.on('whiteboard_presence', (data) => {
      if (!data || data.code !== boardCode) return;
      renderParticipants(data.participants || []);
    });
  }
});
