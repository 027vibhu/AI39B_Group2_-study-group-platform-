document.addEventListener('DOMContentLoaded', () => {
  const toolButtons = document.querySelectorAll('.tool');
  const swatches = document.querySelectorAll('.color-swatch');
  const undoButton = document.querySelector('.sidebar-btn:nth-of-type(1)');
  const redoButton = document.querySelector('.sidebar-btn:nth-of-type(2)');
  const clearButton = document.querySelector('.sidebar-btn:nth-of-type(3)');
  const canvasContainer = document.querySelector('.whiteboard-canvas');
  const placeholder = document.querySelector('.canvas-placeholder');
  const canvas = document.getElementById('whiteboardCanvas');

  if (!canvas || !canvasContainer) return;

  const ctx = canvas.getContext('2d');
  let drawing = false;
  let currentTool = 'Pen';
  let currentColor = '#222243';
  let lastPoint = null;
  const history = [];
  let historyIndex = -1;

  function resizeCanvas() {
    const rect = canvasContainer.getBoundingClientRect();
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    canvas.width = Math.floor(rect.width);
    canvas.height = Math.floor(rect.height);
    ctx.putImageData(imageData, 0, 0);
  }

  function setActiveTool(toolButton) {
    toolButtons.forEach((button) => button.classList.remove('active'));
    toolButton.classList.add('active');
    currentTool = toolButton.textContent.trim();
  }

  function setActiveColor(swatch) {
    swatches.forEach((button) => button.classList.remove('active'));
    swatch.classList.add('active');
    currentColor = window.getComputedStyle(swatch).backgroundColor;
  }

  function pushHistory() {
    history.splice(historyIndex + 1);
    history.push(canvas.toDataURL());
    historyIndex = history.length - 1;
  }

  function restoreHistory(index) {
    const image = new Image();
    image.src = history[index];
    image.onload = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(image, 0, 0);
    };
  }

  function updatePlaceholder() {
    placeholder.style.display = historyIndex === -1 ? 'block' : 'none';
  }

  function startDraw(event) {
    drawing = true;
    lastPoint = getPointerPosition(event);
    ctx.strokeStyle = currentTool === 'Eraser' ? '#ffffff' : currentColor;
    ctx.lineWidth = currentTool === 'Eraser' ? 24 : 4;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.beginPath();
    ctx.moveTo(lastPoint.x, lastPoint.y);
  }

  function draw(event) {
    if (!drawing) return;
    const point = getPointerPosition(event);
    if (currentTool === 'Shape') {
      // quick preview line
      return;
    }
    ctx.lineTo(point.x, point.y);
    ctx.stroke();
    lastPoint = point;
  }

  function stopDraw() {
    if (!drawing) return;
    drawing = false;
    pushHistory();
    updatePlaceholder();
  }

  function getPointerPosition(event) {
    const rect = canvas.getBoundingClientRect();
    const clientX = event.touches ? event.touches[0].clientX : event.clientX;
    const clientY = event.touches ? event.touches[0].clientY : event.clientY;
    return {
      x: clientX - rect.left,
      y: clientY - rect.top,
    };
  }

  toolButtons.forEach((button) => {
    button.addEventListener('click', () => setActiveTool(button));
  });

  swatches.forEach((swatch) => {
    swatch.addEventListener('click', () => setActiveColor(swatch));
  });

  undoButton.addEventListener('click', () => {
    if (historyIndex <= 0) return;
    historyIndex -= 1;
    restoreHistory(historyIndex);
    updatePlaceholder();
  });

  redoButton.addEventListener('click', () => {
    if (historyIndex >= history.length - 1) return;
    historyIndex += 1;
    restoreHistory(historyIndex);
    updatePlaceholder();
  });

  clearButton.addEventListener('click', () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    history.length = 0;
    historyIndex = -1;
    updatePlaceholder();
  });

  canvas.addEventListener('mousedown', startDraw);
  canvas.addEventListener('touchstart', startDraw);
  canvas.addEventListener('mousemove', draw);
  canvas.addEventListener('touchmove', draw);
  canvas.addEventListener('mouseup', stopDraw);
  canvas.addEventListener('mouseleave', stopDraw);
  canvas.addEventListener('touchend', stopDraw);

  window.addEventListener('resize', resizeCanvas);
  resizeCanvas();
  updatePlaceholder();
});
