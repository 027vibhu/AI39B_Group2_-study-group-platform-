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
  const uploadButton = document.getElementById('uploadButton');
  const uploadInput = document.getElementById('uploadInput');
  const zoomInBtn = document.getElementById('zoomInBtn');
  const zoomOutBtn = document.getElementById('zoomOutBtn');
  const zoomResetBtn = document.getElementById('zoomResetBtn');
  const inviteButton = document.getElementById('inviteButton');
  const inviteModal = document.getElementById('inviteModal');
  const inviteLinkInput = document.getElementById('inviteLinkInput');
  const copyInviteLink = document.getElementById('copyInviteLink');
  const closeInviteModal = document.getElementById('closeInviteModal');
  const participantList = document.getElementById('participantList');
  const participantCount = document.getElementById('participantCount');
  const participantCountPanel = document.getElementById('participantCountPanel');
  const participantsToggle = document.getElementById('participantsToggle');
  const participantsPanel = document.getElementById('participantsPanel');

  const config = window.WHITEBOARD || {};
  const boardCode = config.code || '';
  const displayName = config.username || 'Guest';

  // --- State -------------------------------------------------------------
  let selectedTool = 'Pen';
  let selectedShape = 'rectangle';
  let selectedColor = '#111827';
  // Each tool remembers its own stroke width so switching tools restores the
  // size that suits it (a thin pen vs. a broad highlighter).
  const toolStrokes = { Pen: 3, Highlighter: 20, Eraser: 24, Text: 3, Shapes: 3 };
  let selectedStroke = toolStrokes[selectedTool];
  let isDrawing = false;
  let lastPosition = { x: 0, y: 0 };
  let currentPoints = [];

  // --- Object model ------------------------------------------------------
  // The board is the source of truth: an ordered list of objects (z-order =
  // array order) that redraw() replays. Freehand strokes are baked in too but
  // are not selectable; shapes and text can be picked up by the Move tool.
  let objects = [];
  let legacyBackground = null; // <img> painted under objects for old PNG boards
  let selectedId = null;       // currently selected object (Move tool)

  // --- Viewport (infinite canvas) ----------------------------------------
  // Local-only view transform; never synced — each viewer navigates freely.
  //   screenCSS = world * view.scale + view.{x,y}
  // Starts at identity so old boards (stored in screen pixels) map 1:1.
  let view = { x: 0, y: 0, scale: 1 };
  const MIN_SCALE = 0.1;
  const MAX_SCALE = 8;

  // The object currently being drawn (stroke/shape), held in world coords and
  // rendered on top of a full redraw each pointermove. Replaces the old
  // getImageData/putImageData pixel snapshots, which break under a transform.
  let inProgress = null;

  // url -> HTMLImageElement, so image objects only decode once.
  const imageCache = new Map();

  const makeId = () => {
    try {
      if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    } catch (e) { /* ignore */ }
    return `o-${Date.now().toString(36)}-${Math.floor(Math.random() * 1e9).toString(36)}`;
  };

  const TOOL_ICONS = {
    Pen: 'fa-pen',
    Highlighter: 'fa-highlighter',
    Eraser: 'fa-eraser',
    Text: 'fa-font',
    Shapes: 'fa-shapes',
    Move: 'fa-up-down-left-right',
    Hand: 'fa-hand',
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
        state: objects,
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
  // Keep the backing store at device resolution but DON'T bake the draw
  // transform here — redraw() sets it per-frame via applyViewTransform so pan
  // and zoom compose correctly.
  const resizeCanvas = () => {
    if (!canvas || !canvasWrapper || !ctx) return;
    const rect = canvasWrapper.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.max(1, Math.round(rect.width * dpr));
    canvas.height = Math.max(1, Math.round(rect.height * dpr));
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    // Repaint from the object list at the new size (vector redraw stays crisp).
    if (typeof redraw === 'function') redraw();
  };

  // Pointer position in CSS pixels relative to the canvas (screen space).
  const getPointerPosition = (event) => {
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };
  };

  // Screen (CSS px) -> world coords. Objects are stored in world units, so all
  // creation / hit-testing / move math runs through this.
  const screenToWorld = (p) => ({
    x: (p.x - view.x) / view.scale,
    y: (p.y - view.y) / view.scale,
  });

  // Pointer position already mapped into world space.
  const getWorldPosition = (event) => screenToWorld(getPointerPosition(event));

  // Set the per-frame transform: device pixels = (world * scale + pan) * dpr.
  const applyViewTransform = () => {
    const dpr = window.devicePixelRatio || 1;
    ctx.setTransform(
      dpr * view.scale, 0,
      0, dpr * view.scale,
      dpr * view.x, dpr * view.y,
    );
  };

  // --- Eraser size cursor ------------------------------------------------
  // A ring that follows the pointer and matches the current eraser width, so
  // it's obvious how much will be erased before clicking. The eraser strokes
  // with lineWidth = selectedStroke (round cap), so the ring diameter equals
  // the stroke width in CSS pixels — the same units getPointerPosition uses.
  let eraserCursor = null;
  if (canvasWrapper) {
    eraserCursor = document.createElement('div');
    eraserCursor.className = 'wb-eraser-cursor';
    eraserCursor.setAttribute('aria-hidden', 'true');
    canvasWrapper.appendChild(eraserCursor);
  }

  const sizeEraserCursor = () => {
    if (!eraserCursor) return;
    // The eraser width is a world measurement; show its on-screen size so the
    // ring matches what will actually be erased at the current zoom.
    const px = selectedStroke * view.scale;
    eraserCursor.style.width = `${px}px`;
    eraserCursor.style.height = `${px}px`;
  };

  const setEraserMode = (active) => {
    if (canvasWrapper) canvasWrapper.classList.toggle('eraser-active', active);
    if (active) sizeEraserCursor();
    else if (eraserCursor) eraserCursor.classList.remove('visible');
  };

  const trackEraserCursor = (event) => {
    if (selectedTool !== 'Eraser' || !eraserCursor) return;
    const point = getPointerPosition(event);
    eraserCursor.style.left = `${point.x}px`;
    eraserCursor.style.top = `${point.y}px`;
    eraserCursor.classList.add('visible');
  };

  const hideEraserCursor = () => {
    if (eraserCursor) eraserCursor.classList.remove('visible');
  };

  // --- Move mode ---------------------------------------------------------
  // Toggle the grab cursor and clear any selection when leaving the tool.
  const setMoveMode = (active) => {
    if (canvasWrapper) canvasWrapper.classList.toggle('move-active', active);
    if (!active) {
      selectedId = null;
      if (canvasWrapper) {
        canvasWrapper.classList.remove('grabbing');
        canvasWrapper.style.cursor = ''; // drop any handle resize cursor
      }
      if (typeof redraw === 'function') redraw();
    }
  };

  // --- Rendering primitives (shared by local + remote actions) -----------
  const applyStrokeStyle = (tool, color, stroke) => {
    ctx.lineWidth = stroke;
    ctx.globalCompositeOperation = tool === 'Eraser' ? 'destination-out' : 'source-over';
    const strokeColor = tool === 'Eraser' ? '#000000' : color;
    ctx.strokeStyle = tool === 'Highlighter' ? `${strokeColor}66` : strokeColor;
    ctx.fillStyle = tool === 'Highlighter' ? `${strokeColor}44` : strokeColor;
    // The highlighter uses a flat, chisel-style tip (square ends, mitred
    // corners) so it lays down a clean rectangular band over notes. Other
    // tools keep the round nib for smooth freehand strokes.
    if (tool === 'Highlighter') {
      ctx.lineCap = 'butt';
      ctx.lineJoin = 'miter';
    } else {
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
    }
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
  // Shapes are outlined only — never filled — so they sit over notes without
  // hiding what's underneath.
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
      ctx.stroke();
    } else if (shape === 'circle') {
      // A true circle sized by the smaller box dimension, kept in the corner the
      // drag started from so it grows naturally with the cursor.
      const r = Math.min(Math.abs(width), Math.abs(height)) / 2;
      const cx = x + Math.sign(width || 1) * r;
      const cy = y + Math.sign(height || 1) * r;
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.stroke();
    } else if (shape === 'rounded-rectangle') {
      const x0 = Math.min(x, x + width);
      const y0 = Math.min(y, y + height);
      const w = Math.abs(width);
      const h = Math.abs(height);
      const r = Math.min(16, w / 2, h / 2);
      if (ctx.roundRect) {
        ctx.roundRect(x0, y0, w, h, r);
      } else {
        // Manual rounded rect for browsers without ctx.roundRect.
        ctx.moveTo(x0 + r, y0);
        ctx.arcTo(x0 + w, y0, x0 + w, y0 + h, r);
        ctx.arcTo(x0 + w, y0 + h, x0, y0 + h, r);
        ctx.arcTo(x0, y0 + h, x0, y0, r);
        ctx.arcTo(x0, y0, x0 + w, y0, r);
        ctx.closePath();
      }
      ctx.stroke();
    } else if (shape === 'triangle') {
      // Apex at the top-centre, base spanning the bottom of the box.
      const x2 = x + width;
      const y2 = y + height;
      ctx.moveTo(x + width / 2, y);
      ctx.lineTo(x2, y2);
      ctx.lineTo(x, y2);
      ctx.closePath();
      ctx.stroke();
    } else if (shape === 'diamond') {
      const cx = x + width / 2;
      const cy = y + height / 2;
      ctx.moveTo(cx, y);
      ctx.lineTo(x + width, cy);
      ctx.lineTo(cx, y + height);
      ctx.lineTo(x, cy);
      ctx.closePath();
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

  // Draw an image object from the cache, lazy-loading on first sight. The
  // element decodes once; onload triggers a redraw so it appears when ready.
  const renderImage = (obj) => {
    if (!ctx || !obj.url) return;
    let img = imageCache.get(obj.url);
    if (!img) {
      img = new Image();
      img.onload = () => redraw();
      img.src = obj.url;
      imageCache.set(obj.url, img);
    }
    if (img.complete && img.naturalWidth) {
      ctx.save();
      ctx.globalCompositeOperation = 'source-over';
      ctx.drawImage(img, obj.x, obj.y, obj.width, obj.height);
      ctx.restore();
      togglePlaceholder(false);
    }
  };

  // Render a single object through the matching primitive.
  const renderObject = (obj) => {
    if (!obj) return;
    if (obj.type === 'stroke') renderStroke(obj);
    else if (obj.type === 'shape') renderShape(obj);
    else if (obj.type === 'text') renderText(obj);
    else if (obj.type === 'image') renderImage(obj);
  };

  // --- Object geometry (used by Move hit-testing + selection outline) -----
  // Normalized bounding box {x, y, w, h} in CSS pixels, or null for strokes.
  const objectBounds = (obj) => {
    if (!obj) return null;
    if (obj.type === 'shape' || obj.type === 'image') {
      const x = Math.min(obj.x, obj.x + obj.width);
      const y = Math.min(obj.y, obj.y + obj.height);
      return { x, y, w: Math.abs(obj.width), h: Math.abs(obj.height) };
    }
    if (obj.type === 'text') {
      if (!ctx) return { x: obj.x, y: obj.y, w: 0, h: 0 };
      ctx.save();
      ctx.font = `${obj.size}px Arial, sans-serif`;
      const lines = String(obj.text).split('\n');
      let w = 0;
      lines.forEach((line) => { w = Math.max(w, ctx.measureText(line).width); });
      ctx.restore();
      return { x: obj.x, y: obj.y, w, h: lines.length * obj.size * 1.15 };
    }
    return null; // strokes are not selectable
  };

  // Distance from point p to segment a-b, for line/arrow hit testing.
  const distToSegment = (p, ax, ay, bx, by) => {
    const dx = bx - ax;
    const dy = by - ay;
    const lenSq = dx * dx + dy * dy;
    let t = lenSq ? ((p.x - ax) * dx + (p.y - ay) * dy) / lenSq : 0;
    t = Math.max(0, Math.min(1, t));
    const cx = ax + t * dx;
    const cy = ay + t * dy;
    return Math.hypot(p.x - cx, p.y - cy);
  };

  // Topmost selectable object under the point, or null. Iterates back-to-front.
  const hitTest = (point) => {
    for (let i = objects.length - 1; i >= 0; i -= 1) {
      const obj = objects[i];
      if (obj.type === 'shape' && (obj.shape === 'line' || obj.shape === 'arrow')) {
        const tol = Math.max(6, obj.stroke || 0);
        if (distToSegment(point, obj.x, obj.y, obj.x + obj.width, obj.y + obj.height) <= tol) {
          return obj;
        }
        continue;
      }
      const b = objectBounds(obj);
      if (!b) continue;
      const pad = 4; // a little slack so thin shapes are easy to grab
      if (point.x >= b.x - pad && point.x <= b.x + b.w + pad
          && point.y >= b.y - pad && point.y <= b.y + b.h + pad) {
        return obj;
      }
    }
    return null;
  };

  // --- Full redraw from the object list ----------------------------------
  const clearPixels = () => {
    if (!canvas || !ctx) return;
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.restore();
  };

  // Margin between an object's bounds and its dashed selection box / handles.
  const SEL_MARGIN = 6;

  // Corner handle geometry. `hx/hy` is where the handle is drawn and grabbed
  // (just outside the dashed box); `ax/ay` is the opposite *true* corner that
  // stays pinned while that handle is dragged, so resizing never drifts.
  const handlePositions = (b) => {
    const m = SEL_MARGIN;
    return [
      { key: 'nw', hx: b.x - m,       hy: b.y - m,       ax: b.x + b.w, ay: b.y + b.h },
      { key: 'ne', hx: b.x + b.w + m, hy: b.y - m,       ax: b.x,       ay: b.y + b.h },
      { key: 'sw', hx: b.x - m,       hy: b.y + b.h + m, ax: b.x + b.w, ay: b.y },
      { key: 'se', hx: b.x + b.w + m, hy: b.y + b.h + m, ax: b.x,       ay: b.y },
    ];
  };

  // The selected object, but only if it supports box resizing: images (incl.
  // rasterized PDF pages), text, and boxed shapes. Line/arrow are excluded
  // since they have no meaningful bounding box to drag.
  const resizableSelected = () => {
    if (!selectedId) return null;
    const obj = objects.find((o) => o.id === selectedId);
    if (!obj) return null;
    if (obj.type === 'image' || obj.type === 'text') return obj;
    if (obj.type === 'shape' && obj.shape !== 'line' && obj.shape !== 'arrow') return obj;
    return null;
  };

  const RESIZE_HANDLE = 9; // on-screen handle size in CSS px

  // White corner squares for the resize handles. Sizes are divided by the view
  // scale so they stay a constant size on screen at any zoom level.
  const drawResizeHandles = (b) => {
    const s = RESIZE_HANDLE / view.scale;
    const half = s / 2;
    ctx.save();
    ctx.globalCompositeOperation = 'source-over';
    ctx.fillStyle = '#ffffff';
    ctx.strokeStyle = '#4f46e5';
    ctx.lineWidth = 1.5 / view.scale;
    handlePositions(b).forEach((h) => {
      ctx.beginPath();
      ctx.rect(h.hx - half, h.hy - half, s, s);
      ctx.fill();
      ctx.stroke();
    });
    ctx.restore();
  };

  const drawSelectionOutline = () => {
    if (!selectedId || !ctx) return;
    const obj = objects.find((o) => o.id === selectedId);
    const b = objectBounds(obj);
    if (!b) return;
    const m = SEL_MARGIN;
    ctx.save();
    ctx.globalCompositeOperation = 'source-over';
    ctx.strokeStyle = '#4f46e5';
    // Scale line metrics by the view so the outline stays crisp at any zoom.
    ctx.lineWidth = 1.5 / view.scale;
    ctx.setLineDash([6 / view.scale, 4 / view.scale]);
    ctx.strokeRect(b.x - m, b.y - m, b.w + m * 2, b.h + m * 2);
    ctx.restore();
    // Show drag handles for objects that can be resized.
    if (resizableSelected()) drawResizeHandles(b);
  };

  const redraw = () => {
    if (!ctx) return;
    clearPixels();
    applyViewTransform();
    if (legacyBackground) {
      // Old boards were authored in screen pixels at the wrapper's size; drawing
      // it at that size in world space keeps it 1:1 at the default view and lets
      // it pan/zoom with the board.
      const rect = canvasWrapper.getBoundingClientRect();
      ctx.drawImage(legacyBackground, 0, 0, rect.width, rect.height);
    }
    objects.forEach(renderObject);
    if (inProgress) renderObject(inProgress);
    drawSelectionOutline();
    togglePlaceholder(objects.length === 0 && !legacyBackground && !inProgress);
  };

  const applyRemoteAction = (action, payload) => {
    if (!payload) return;
    if (action === 'move') {
      // Any positioned object (shape, text, image) moves the same way.
      const obj = objects.find((o) => o.id === payload.id);
      if (obj) {
        obj.x = payload.x;
        obj.y = payload.y;
        redraw();
      }
      return;
    }
    if (action === 'resize') {
      // Geometry update from another viewer: apply whichever fields are present
      // (images/shapes carry width/height; text carries size).
      const obj = objects.find((o) => o.id === payload.id);
      if (obj) {
        if (payload.x !== undefined) obj.x = payload.x;
        if (payload.y !== undefined) obj.y = payload.y;
        if (payload.width !== undefined) obj.width = payload.width;
        if (payload.height !== undefined) obj.height = payload.height;
        if (payload.size !== undefined) obj.size = payload.size;
        redraw();
      }
      return;
    }
    if (action === 'delete') {
      objects = objects.filter((o) => o.id !== payload.id);
      if (selectedId === payload.id) selectedId = null;
      redraw();
      return;
    }
    // stroke / shape / text / image: add the object (dedupe by id) and redraw.
    if (action === 'stroke' || action === 'shape' || action === 'text' || action === 'image') {
      if (!payload.id || !objects.some((o) => o.id === payload.id)) {
        objects.push(payload);
      }
      // Ensure remote image URLs start decoding so they paint on the next frame.
      if (action === 'image' && payload.url && !imageCache.has(payload.url)) {
        const img = new Image();
        img.onload = () => redraw();
        img.src = payload.url;
        imageCache.set(payload.url, img);
      }
      redraw();
    }
  };

  // Load a persisted board. New format is an array of objects; the legacy
  // format was a PNG data-URL string — render that once as a baked background
  // so old boards stay visible while new edits become movable objects on top.
  const loadState = (state) => {
    if (Array.isArray(state)) {
      objects = state.filter(Boolean);
      legacyBackground = null;
      redraw();
      return;
    }
    if (typeof state === 'string' && state.startsWith('data:image')) {
      const img = new Image();
      img.onload = () => {
        legacyBackground = img;
        redraw();
      };
      img.src = state;
    }
  };

  const clearCanvas = (local = true) => {
    if (!canvas || !ctx) return;
    removeTextEditor();
    objects = [];
    legacyBackground = null;
    selectedId = null;
    inProgress = null;
    resizing = null;
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
    // dataset.x/y/size are stored in WORLD units so the object is zoom-agnostic.
    const x = parseFloat(textEditor.dataset.x);
    const y = parseFloat(textEditor.dataset.y);
    const size = parseFloat(textEditor.dataset.size);
    const color = textEditor.dataset.color;
    removeTextEditor();
    if (!text) return;
    const obj = { id: makeId(), type: 'text', text, x, y, color, size };
    objects.push(obj);
    redraw();
    emitAction('text', obj);
  };

  // `screen` is the CSS-pixel pointer position (where the editor floats);
  // `world` is the same point in world units (what the object stores).
  const openTextEditor = (screen, world) => {
    removeTextEditor();
    const size = Math.max(14, selectedStroke * 5); // world-space font size
    textEditor = document.createElement('textarea');
    textEditor.className = 'wb-text-input';
    textEditor.rows = 1;
    textEditor.style.left = `${screen.x}px`;
    textEditor.style.top = `${screen.y}px`;
    textEditor.style.color = selectedColor;
    // Show the on-screen size so the editing preview matches the rendered glyphs.
    textEditor.style.fontSize = `${size * view.scale}px`;
    textEditor.dataset.x = world.x;
    // canvas baseline is "top" so align the editor's text box to the same y.
    textEditor.dataset.y = world.y;
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
  // All geometry below is in WORLD coords. The live preview is held in
  // `inProgress` and painted on top of a full redraw() each move — no pixel
  // snapshots, so everything composes correctly under pan/zoom.
  const beginDrawing = (event) => {
    if (!canvas || !ctx) return;
    if (event.button !== undefined && event.button !== 0) return; // left button only
    if (isPanGesture(event)) { beginPan(event); return; }      // Hand tool / spacebar
    const point = getWorldPosition(event);

    if (selectedTool === 'Move') {
      beginMove(point, event);
      return;
    }

    if (selectedTool === 'Text') {
      openTextEditor(getPointerPosition(event), point);
      return;
    }

    isDrawing = true;
    lastPosition = point;
    currentPoints = [point];

    if (selectedTool === 'Shapes') {
      inProgress = {
        type: 'shape', shape: selectedShape, color: selectedColor,
        stroke: selectedStroke, x: point.x, y: point.y, width: 0, height: 0,
      };
    } else {
      inProgress = {
        type: 'stroke', tool: selectedTool, color: selectedColor,
        stroke: selectedStroke, points: currentPoints,
      };
    }

    togglePlaceholder(false);
    redraw();
    try { canvas.setPointerCapture(event.pointerId); } catch (e) { /* ignore */ }
  };

  const drawMove = (event) => {
    if (isPanning) { panDrag(event); return; }
    if (selectedTool === 'Move') {
      if (resizing) { resizeDrag(getWorldPosition(event)); return; }
      moveDrag(getWorldPosition(event));
      return;
    }
    if (!isDrawing || !canvas || !ctx || !inProgress) return;
    const point = getWorldPosition(event);

    if (selectedTool === 'Shapes') {
      inProgress.width = point.x - lastPosition.x;
      inProgress.height = point.y - lastPosition.y;
    } else {
      currentPoints.push(point);
      lastPosition = point;
    }
    redraw();
  };

  const endDrawing = (event) => {
    if (isPanning) { endPan(event); return; }
    if (selectedTool === 'Move') {
      endMove(event);
      return;
    }
    if (!isDrawing || !canvas || !ctx) return;
    const point = getWorldPosition(event);

    if (selectedTool === 'Shapes') {
      const obj = {
        id: makeId(),
        type: 'shape',
        shape: selectedShape,
        color: selectedColor,
        stroke: selectedStroke,
        x: lastPosition.x,
        y: lastPosition.y,
        width: point.x - lastPosition.x,
        height: point.y - lastPosition.y,
      };
      objects.push(obj);
      emitAction('shape', obj);
    } else {
      const obj = {
        id: makeId(),
        type: 'stroke',
        tool: selectedTool,
        color: selectedColor,
        stroke: selectedStroke,
        points: currentPoints,
      };
      objects.push(obj);
      emitAction('stroke', obj);
    }

    inProgress = null;
    isDrawing = false;
    currentPoints = [];
    redraw();
    if (event.pointerId !== undefined) {
      try { canvas.releasePointerCapture(event.pointerId); } catch (e) { /* ignore */ }
    }
  };

  // --- Move tool ---------------------------------------------------------
  // Dragging a selected shape/text. We keep a grab offset so the object
  // doesn't jump its origin to the cursor on pickup.
  let movingObj = null;
  let grabOffset = { x: 0, y: 0 };
  let moveEmitTimer = null;

  const emitMoveThrottled = (obj) => {
    if (moveEmitTimer) return;
    moveEmitTimer = setTimeout(() => { moveEmitTimer = null; }, 40);
    emitAction('move', { id: obj.id, x: obj.x, y: obj.y });
  };

  const beginMove = (point, event) => {
    // A corner handle of the already-selected object starts a resize instead
    // of a move/re-select.
    const handle = hitResizeHandle(point);
    if (handle) { beginResize(handle, event); return; }
    const hit = hitTest(point);
    selectedId = hit ? hit.id : null;
    movingObj = hit || null;
    if (hit) {
      grabOffset = { x: point.x - hit.x, y: point.y - hit.y };
      if (canvasWrapper) canvasWrapper.classList.add('grabbing');
      try { canvas.setPointerCapture(event.pointerId); } catch (e) { /* ignore */ }
    }
    redraw();
  };

  const moveDrag = (point) => {
    if (!movingObj) return;
    movingObj.x = point.x - grabOffset.x;
    movingObj.y = point.y - grabOffset.y;
    redraw();
    emitMoveThrottled(movingObj);
  };

  const endMove = (event) => {
    if (resizing) { endResize(event); return; }
    if (canvasWrapper) canvasWrapper.classList.remove('grabbing');
    if (movingObj) {
      // Emit the final resting position (unthrottled) and persist.
      emitAction('move', { id: movingObj.id, x: movingObj.x, y: movingObj.y });
      scheduleStateSave();
    }
    movingObj = null;
    if (event && event.pointerId !== undefined) {
      try { canvas.releasePointerCapture(event.pointerId); } catch (e) { /* ignore */ }
    }
  };

  // Delete the selected object with Delete/Backspace while Move is active.
  const deleteSelected = () => {
    if (!selectedId) return;
    const id = selectedId;
    objects = objects.filter((o) => o.id !== id);
    selectedId = null;
    movingObj = null;
    redraw();
    emitAction('delete', { id });
    scheduleStateSave();
  };

  // --- Resize (corner handles on the Move tool) --------------------------
  // Reuses the Move tool: when a resizable object is selected, dragging one of
  // its corner handles resizes it instead of moving it. Images (and PDF pages)
  // keep their aspect ratio; text scales its font size; shapes resize freely.
  let resizing = null;     // { obj, anchor:{x,y}, startBounds, startSize }
  const RESIZE_HIT = 12;   // grab tolerance around a handle, in CSS px

  // If the pointer is over a handle of the selected object, return the resize
  // descriptor (object + pinned anchor corner + handle key); otherwise null.
  const hitResizeHandle = (worldPoint) => {
    const obj = resizableSelected();
    if (!obj) return null;
    const b = objectBounds(obj);
    if (!b) return null;
    const tol = RESIZE_HIT / view.scale;
    for (const h of handlePositions(b)) {
      if (Math.abs(worldPoint.x - h.hx) <= tol && Math.abs(worldPoint.y - h.hy) <= tol) {
        return { obj, anchor: { x: h.ax, y: h.ay }, key: h.key };
      }
    }
    return null;
  };

  let resizeEmitTimer = null;
  const resizePayload = (obj) => (obj.type === 'text'
    ? { id: obj.id, x: obj.x, y: obj.y, size: obj.size }
    : { id: obj.id, x: obj.x, y: obj.y, width: obj.width, height: obj.height });

  const emitResizeThrottled = (obj) => {
    if (resizeEmitTimer) return;
    resizeEmitTimer = setTimeout(() => { resizeEmitTimer = null; }, 40);
    emitAction('resize', resizePayload(obj));
  };

  const beginResize = (info, event) => {
    resizing = {
      obj: info.obj,
      anchor: info.anchor,
      startBounds: objectBounds(info.obj),
      startSize: info.obj.size, // text only; harmless otherwise
    };
    selectedId = info.obj.id;
    if (canvasWrapper) canvasWrapper.classList.add('grabbing');
    try { canvas.setPointerCapture(event.pointerId); } catch (e) { /* ignore */ }
    redraw();
  };

  const resizeDrag = (point) => {
    if (!resizing) return;
    const { obj, anchor, startBounds, startSize } = resizing;
    const ax = anchor.x;
    const ay = anchor.y;
    if (obj.type === 'text') {
      // Scale the font size by the larger axis ratio, then re-pin the anchor
      // corner so the opposite side stays put while the box grows/shrinks.
      const w = Math.max(1, Math.abs(point.x - ax));
      const h = Math.max(1, Math.abs(point.y - ay));
      const factor = Math.max(w / Math.max(1, startBounds.w), h / Math.max(1, startBounds.h));
      obj.size = Math.max(8, startSize * factor);
      const nb = objectBounds(obj);
      obj.x = point.x < ax ? ax - nb.w : ax;
      obj.y = point.y < ay ? ay - nb.h : ay;
    } else {
      let w = Math.max(8, Math.abs(point.x - ax));
      let h = Math.max(8, Math.abs(point.y - ay));
      if (obj.type === 'image' && startBounds.h) {
        // Lock to the original aspect ratio so images/PDF pages aren't squished.
        const aspect = startBounds.w / startBounds.h;
        if (w / h > aspect) w = h * aspect; else h = w / aspect;
      }
      obj.x = point.x < ax ? ax - w : ax;
      obj.y = point.y < ay ? ay - h : ay;
      obj.width = w;
      obj.height = h;
    }
    redraw();
    emitResizeThrottled(obj);
  };

  const endResize = (event) => {
    if (!resizing) return;
    // Emit the final geometry (unthrottled) and persist.
    emitAction('resize', resizePayload(resizing.obj));
    scheduleStateSave();
    resizing = null;
    if (canvasWrapper) canvasWrapper.classList.remove('grabbing');
    if (event && event.pointerId !== undefined) {
      try { canvas.releasePointerCapture(event.pointerId); } catch (e) { /* ignore */ }
    }
  };

  // Hover feedback: show a diagonal resize cursor over a handle while the Move
  // tool is active and nothing is being dragged.
  const updateMoveCursor = (event) => {
    if (selectedTool !== 'Move' || resizing || movingObj || !canvasWrapper) return;
    const hit = hitResizeHandle(getWorldPosition(event));
    canvasWrapper.style.cursor = hit
      ? ((hit.key === 'nw' || hit.key === 'se') ? 'nwse-resize' : 'nesw-resize')
      : '';
  };

  // --- Pan & zoom (Figma-like) -------------------------------------------
  let isSpacePan = false;   // Space held -> temporary pan regardless of tool
  let isPanning = false;    // a pan-drag is in progress
  let panStart = { x: 0, y: 0, viewX: 0, viewY: 0 };

  // A pointerdown should pan when the Hand tool is active or Space is held.
  const isPanGesture = () => selectedTool === 'Hand' || isSpacePan;

  const setGrabbing = (on) => {
    if (canvasWrapper) canvasWrapper.classList.toggle('grabbing', on);
  };

  const beginPan = (event) => {
    isPanning = true;
    const p = getPointerPosition(event);
    panStart = { x: p.x, y: p.y, viewX: view.x, viewY: view.y };
    setGrabbing(true);
    try { canvas.setPointerCapture(event.pointerId); } catch (e) { /* ignore */ }
  };

  const panDrag = (event) => {
    if (!isPanning) return;
    const p = getPointerPosition(event);
    view.x = panStart.viewX + (p.x - panStart.x);
    view.y = panStart.viewY + (p.y - panStart.y);
    redraw();
  };

  const endPan = (event) => {
    isPanning = false;
    setGrabbing(false);
    if (event && event.pointerId !== undefined) {
      try { canvas.releasePointerCapture(event.pointerId); } catch (e) { /* ignore */ }
    }
  };

  // Zoom by `factor` while keeping the world point under `screen` fixed.
  const zoomAt = (screen, factor) => {
    const next = Math.min(MAX_SCALE, Math.max(MIN_SCALE, view.scale * factor));
    if (next === view.scale) return;
    const wx = (screen.x - view.x) / view.scale;
    const wy = (screen.y - view.y) / view.scale;
    view.scale = next;
    view.x = screen.x - wx * view.scale;
    view.y = screen.y - wy * view.scale;
    sizeEraserCursor();
    updateZoomLabel();
    redraw();
  };

  const stageCenter = () => {
    const rect = (canvasWrapper || canvas).getBoundingClientRect();
    return { x: rect.width / 2, y: rect.height / 2 };
  };

  const resetView = () => {
    view = { x: 0, y: 0, scale: 1 };
    sizeEraserCursor();
    updateZoomLabel();
    redraw();
  };

  const updateZoomLabel = () => {
    if (zoomResetBtn) zoomResetBtn.textContent = `${Math.round(view.scale * 100)}%`;
  };

  // Wheel: plain wheel pans; Ctrl/⌘ (and trackpad pinch) zooms around the cursor.
  const onWheel = (event) => {
    event.preventDefault();
    if (event.ctrlKey || event.metaKey) {
      const factor = Math.exp(-event.deltaY * 0.0015);
      zoomAt(getPointerPosition(event), factor);
    } else {
      view.x -= event.deltaX;
      view.y -= event.deltaY;
      redraw();
    }
  };

  if (canvasWrapper) {
    canvasWrapper.addEventListener('wheel', onWheel, { passive: false });
  }
  if (zoomInBtn) zoomInBtn.addEventListener('click', () => zoomAt(stageCenter(), 1.2));
  if (zoomOutBtn) zoomOutBtn.addEventListener('click', () => zoomAt(stageCenter(), 1 / 1.2));
  if (zoomResetBtn) zoomResetBtn.addEventListener('click', resetView);

  // --- Tool / shape / color / stroke selection ---------------------------
  toolButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      selectedTool = btn.dataset.tool;
      activateButtonGroup(toolButtons, btn);
      setEraserMode(selectedTool === 'Eraser');
      setMoveMode(selectedTool === 'Move');
      if (canvasWrapper) canvasWrapper.classList.toggle('hand-active', selectedTool === 'Hand');

      // Restore this tool's own remembered stroke width and sync the slider UI.
      selectedStroke = toolStrokes[selectedTool] ?? selectedStroke;
      if (strokeRange) strokeRange.value = String(selectedStroke);
      if (strokeValue) strokeValue.textContent = `${selectedStroke} px`;
      sizeEraserCursor();

      // Leaving Shapes always closes the flyout; the dedicated Shapes-button
      // handler below owns opening/toggling it (both listeners fire on that one
      // button, so forcing it open here would just fight that toggle).
      if (selectedTool !== 'Shapes') setShapesFlyout(false);

      const hints = {
        Pen: 'Drag to draw freehand',
        Highlighter: 'Drag to highlight (semi-transparent)',
        Eraser: 'Drag over strokes to erase them',
        Text: 'Click on the canvas, then type. Enter to place, Esc to cancel',
        Shapes: 'Pick a shape, then drag to size it',
        Move: 'Drag to move; drag a corner handle to resize. Del removes it',
        Hand: 'Drag to pan the canvas. Scroll to pan, Ctrl/⌘+scroll to zoom',
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
        setEraserMode(false);
        // Restore the Shapes tool's own remembered stroke width.
        selectedStroke = toolStrokes.Shapes ?? selectedStroke;
        if (strokeRange) strokeRange.value = String(selectedStroke);
        if (strokeValue) strokeValue.textContent = `${selectedStroke} px`;
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
      toolStrokes[selectedTool] = selectedStroke; // remember per tool
      if (strokeValue) strokeValue.textContent = `${selectedStroke} px`;
      sizeEraserCursor();
      updateStatus();
    });
  }

  // --- Canvas events -----------------------------------------------------
  if (canvas) {
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    canvas.addEventListener('pointerdown', beginDrawing);
    canvas.addEventListener('pointermove', drawMove);
    canvas.addEventListener('pointermove', trackEraserCursor);
    canvas.addEventListener('pointermove', updateMoveCursor);
    canvas.addEventListener('pointerup', endDrawing);
    canvas.addEventListener('pointerleave', endDrawing);
    canvas.addEventListener('pointerleave', hideEraserCursor);
    canvas.addEventListener('pointercancel', endDrawing);
    canvas.addEventListener('pointercancel', hideEraserCursor);
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

  // --- Image & PDF upload ------------------------------------------------
  // Upload an image blob to the server; returns its served URL (or null).
  const uploadBlob = async (blob, filename) => {
    const form = new FormData();
    form.append('file', blob, filename);
    try {
      const res = await fetch(`/api/whiteboards/${boardCode}/upload`, {
        method: 'POST',
        body: form,
      });
      const data = await res.json();
      if (!res.ok || data.status !== 'success') {
        console.error('Upload failed:', data && data.message);
        return null;
      }
      return data.url;
    } catch (e) {
      console.error('Upload error:', e);
      return null;
    }
  };

  // Place an image object at a given world point, fitting it within maxWorld so
  // huge files don't dominate the board. Decodes the URL to read natural size.
  const MAX_IMAGE_WORLD = 600;
  const placeImageObject = (url, worldPoint, stackOffsetY = 0) => new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const nw = img.naturalWidth || 1;
      const nh = img.naturalHeight || 1;
      const fit = Math.min(1, MAX_IMAGE_WORLD / Math.max(nw, nh));
      const width = nw * fit;
      const height = nh * fit;
      const obj = {
        id: makeId(),
        type: 'image',
        url,
        x: worldPoint.x - width / 2,
        y: worldPoint.y + stackOffsetY,
        width,
        height,
      };
      imageCache.set(url, img);
      objects.push(obj);
      redraw();
      emitAction('image', obj);
      resolve(height);
    };
    img.onerror = () => resolve(0);
    img.src = url;
  });

  // Rasterize a PDF into per-page PNG blobs (pdf.js), upload each, and stack the
  // pages vertically from the viewport center.
  const handlePdf = async (file, centerWorld) => {
    if (!window.pdfjsLib) {
      console.error('pdf.js not loaded');
      return;
    }
    const buf = await file.arrayBuffer();
    const pdf = await window.pdfjsLib.getDocument({ data: buf }).promise;
    let stackY = -200; // start a little above center so the first page is visible
    const GAP = 24;
    for (let n = 1; n <= pdf.numPages; n += 1) {
      const page = await pdf.getPage(n);
      const viewport = page.getViewport({ scale: 2 });
      const off = document.createElement('canvas');
      off.width = Math.ceil(viewport.width);
      off.height = Math.ceil(viewport.height);
      const offCtx = off.getContext('2d');
      // eslint-disable-next-line no-await-in-loop
      await page.render({ canvasContext: offCtx, viewport }).promise;
      // eslint-disable-next-line no-await-in-loop
      const blob = await new Promise((r) => off.toBlob(r, 'image/png'));
      if (!blob) continue;
      // eslint-disable-next-line no-await-in-loop
      const url = await uploadBlob(blob, `page-${n}.png`);
      if (!url) continue;
      // eslint-disable-next-line no-await-in-loop
      const placedHeight = await placeImageObject(url, centerWorld, stackY);
      stackY += placedHeight + GAP;
    }
  };

  const handleFiles = async (files) => {
    if (!files || !files.length || !boardCode) return;
    const center = screenToWorld(stageCenter());
    for (const file of files) {
      if (file.type === 'application/pdf') {
        // eslint-disable-next-line no-await-in-loop
        await handlePdf(file, center);
      } else if (file.type.startsWith('image/')) {
        // eslint-disable-next-line no-await-in-loop
        const url = await uploadBlob(file, file.name);
        // eslint-disable-next-line no-await-in-loop
        if (url) await placeImageObject(url, center);
      }
    }
  };

  if (uploadButton && uploadInput) {
    uploadButton.addEventListener('click', () => uploadInput.click());
    uploadInput.addEventListener('change', () => {
      handleFiles(Array.from(uploadInput.files || []));
      uploadInput.value = ''; // allow re-selecting the same file
    });
  }

  // --- Invite panel ------------------------------------------------------
  // Reuses the floating glass .whiteboard-side shell, so it toggles with the
  // same .open class as the Participants panel (and the two are mutually
  // exclusive since both anchor to the top-right).
  const openInviteModal = () => {
    if (!inviteModal || !inviteLinkInput) return;
    setParticipantsPanel(false);
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
  // Close when clicking outside the panel and its trigger button.
  document.addEventListener('click', (event) => {
    if (!inviteModal || !inviteModal.classList.contains('open')) return;
    if (inviteModal.contains(event.target)) return;
    if (inviteButton && inviteButton.contains(event.target)) return;
    closeInviteDialog();
  });

  // --- Participants panel toggle -----------------------------------------
  const setParticipantsPanel = (open) => {
    if (!participantsPanel) return;
    participantsPanel.classList.toggle('open', open);
    participantsPanel.setAttribute('aria-hidden', open ? 'false' : 'true');
    if (participantsToggle) participantsToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  };
  if (participantsToggle) {
    participantsToggle.addEventListener('click', () => {
      const open = !participantsPanel.classList.contains('open');
      if (open) closeInviteDialog(); // the two top-right panels are mutually exclusive
      setParticipantsPanel(open);
    });
  }
  // Close when clicking outside the panel/button.
  document.addEventListener('click', (event) => {
    if (!participantsPanel || !participantsPanel.classList.contains('open')) return;
    if (participantsPanel.contains(event.target)) return;
    if (participantsToggle && participantsToggle.contains(event.target)) return;
    setParticipantsPanel(false);
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeInviteDialog();
      setParticipantsPanel(false);
      if (selectedId) { selectedId = null; redraw(); }
      return;
    }
    // Spacebar temporarily switches to pan-drag — but not while typing.
    if (event.code === 'Space' && !isSpacePan) {
      const tag = (event.target && event.target.tagName) || '';
      if (tag === 'INPUT' || tag === 'TEXTAREA' || textEditor) return;
      event.preventDefault();
      isSpacePan = true;
      if (canvasWrapper) canvasWrapper.classList.add('space-pan');
      return;
    }
    // Delete the selected object (Move tool) — but never while typing in a
    // text box or input field.
    if ((event.key === 'Delete' || event.key === 'Backspace')
        && selectedId && !textEditor) {
      const tag = (event.target && event.target.tagName) || '';
      if (tag === 'INPUT' || tag === 'TEXTAREA') return;
      event.preventDefault();
      deleteSelected();
    }
  });

  document.addEventListener('keyup', (event) => {
    if (event.code === 'Space') {
      isSpacePan = false;
      if (canvasWrapper) canvasWrapper.classList.remove('space-pan');
      if (isPanning) endPan(event);
    }
  });

  // --- Participants panel ------------------------------------------------
  const renderParticipants = (participants) => {
    const names = participants && participants.length ? participants : [displayName];
    if (participantCount) participantCount.textContent = names.length;
    if (participantCountPanel) participantCountPanel.textContent = names.length;
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
      loadState(data.state);
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
