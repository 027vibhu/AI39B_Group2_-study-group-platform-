# Whiteboard: Infinite Canvas + Image/PDF Upload

## Context

The whiteboard today is a **fixed, screen-sized surface**. Every object (stroke points, shape x/y, text) is stored in **screen-pixel coordinates** and the `<canvas>` is sized 1:1 to the visible stage (`resizeCanvas` in `whiteboard.js`). There is no pan, no zoom, and no way to bring in external content — so a study group runs out of room fast and can't drop in a lecture slide or PDF.

This change makes the board an **infinite, pannable, zoomable canvas (Figma-like)** and adds **image + PDF upload**. PDFs are rasterized client-side (pdf.js) into per-page PNGs and placed as movable image objects. Uploaded files are stored on the server (`static/uploads/whiteboard/`) and only their **URL** is kept in board state, so the synced/persisted JSON stays small.

The foundational piece is a **world-coordinate model with a viewport transform** (`pan {x,y}` + `scale`). Once objects live in world space, image/PDF is just a new object type that rides along, and pan/zoom is purely a local view concern (never synced — each viewer navigates independently).

### Decisions locked in
- **PDF:** rasterize pages → PNG → upload → drop as image objects (pdf.js via CDN).
- **Navigation:** wheel pans, Ctrl/⌘+wheel (and trackpad pinch) zooms around cursor, Hand tool + spacebar-drag pans, on-screen zoom controls.
- **Storage:** multipart upload to `static/uploads/whiteboard/`; board state stores the URL only.

---

## Backward compatibility (important)

Old boards persisted their objects in screen pixels. With the viewport starting at `pan = {0,0}, scale = 1`, **world coords map 1:1 to the old screen coords**, so existing state and the legacy-PNG background load unchanged — no data migration needed.

---

## Part 1 — Frontend: world coordinates + viewport (the refactor)

**File: `app/static/js/whiteboard.js`**

1. **Viewport state** (local only, never emitted):
   ```js
   let view = { x: 0, y: 0, scale: 1 };   // screenCSS = world*scale + view.{x,y}
   const MIN_SCALE = 0.1, MAX_SCALE = 8;
   ```
   Optionally persist `view` to `localStorage` keyed by board code for convenience (nice-to-have).

2. **Coordinate helpers** (add near `getPointerPosition`):
   - `screenToWorld(p)` → `{ x: (p.x - view.x)/view.scale, y: (p.y - view.y)/view.scale }`
   - Replace every `getPointerPosition(event)` use that feeds object creation / hit-testing / move with `screenToWorld(getPointerPosition(event))`. Objects are stored in **world** units.

3. **Apply the transform in `redraw`** instead of relying on the DPR-only transform:
   - In `resizeCanvas`, keep `canvas.width/height` at `rect*dpr` but stop baking the draw transform there; set it per-frame.
   - New `applyViewTransform()`: `ctx.setTransform(dpr*view.scale, 0, 0, dpr*view.scale, dpr*view.x, dpr*view.y)`.
   - `redraw()` → `clearPixels()` (device space) → `applyViewTransform()` → draw `legacyBackground` + objects in world coords → `drawSelectionOutline()`.

4. **Replace the fragile live-preview pixel snapshots** (`getImageData`/`putImageData` for Shapes & Highlighter, and segment-by-segment pen drawing in `beginDrawing`/`drawMove`). Those operate in device pixels and break under a transform. Switch to an **in-progress-object redraw** model:
   - Keep `let inProgress = null` holding the object being drawn (stroke/shape/text-preview) in world coords.
   - On each `pointermove`, update `inProgress` and call `redraw()`, then render `inProgress` on top. This unifies all rendering through the view transform and deletes the snapshot logic. (A full redraw per move is acceptable at this scale and removes a class of bugs.)

5. **Eraser cursor ring** (`wb-eraser-cursor`, a DOM element in CSS px): keep positioning in screen space, but set its on-screen diameter to `selectedStroke * view.scale` so it visually matches the erased world width.

6. **Erasing under zoom:** the eraser remains a `destination-out` stroke stored in world coords; vector replay in `redraw` already composites correctly within the transform.

---

## Part 2 — Frontend: pan & zoom (Figma-like)

**Files: `whiteboard.js`, `whiteboard.html`, `whiteboard.css`**

1. **Hand tool** — add a dock button `data-tool="Hand"` (icon `fa-hand`) next to Move. When active, canvas cursor = `grab`/`grabbing`; pointer-drag updates `view.x/y` and `redraw()`. Reuse the existing tool-activation flow in the `toolButtons` handler.

2. **Spacebar-pan** — holding Space temporarily switches to pan-drag regardless of active tool (track `isSpacePan` in keydown/keyup; guard against firing while typing in the text editor / inputs, mirroring the existing Delete-key guard).

3. **Wheel handler** on `canvasWrapper` (`{ passive: false }`):
   - Plain wheel → pan: `view.x -= e.deltaX; view.y -= e.deltaY`.
   - `e.ctrlKey || e.metaKey` (also trackpad pinch) → **zoom around cursor**: compute world point under the pointer, apply `scale *= factor` clamped to `[MIN,MAX]`, then adjust `view.x/y` so that world point stays under the cursor.
   - `e.preventDefault()` and `redraw()`.

4. **Zoom controls** — a small floating panel (bottom-right of the stage) with `−`, current `%`, `+`, and a reset/“fit” button. Buttons zoom around the viewport center; reset returns to `{0,0,1}`. New markup in `whiteboard.html`, styled in `whiteboard.css` reusing the existing glass tokens (`--glass-bg`, etc., like `.whiteboard-statusbar`).

---

## Part 3 — Frontend: image & PDF upload

**Files: `whiteboard.html`, `whiteboard.js`, `whiteboard.css`**

1. **Upload button** in the topbar actions (near Invite), icon `fa-image` / `fa-file-arrow-up`, opening a hidden `<input type="file" accept="image/*,application/pdf" multiple>`.

2. **Image object type** — new object `{ id, type:'image', url, x, y, width, height }` (world units).
   - **Image cache:** `const imageCache = new Map()` (url → `HTMLImageElement`). `renderObject` gains an `'image'` branch: draw cached image if loaded; otherwise lazy-load and call `redraw()` `onload`.
   - `objectBounds` gains an `'image'` case returning its box → **Move tool + Delete already work** via existing `hitTest`/`drawSelectionOutline`.
   - *(Stretch)* corner resize handles for selected images; first cut ships move + delete only.

3. **Upload flow (images):**
   - `POST` multipart to `/api/whiteboards/<code>/upload` → `{ url, width, height }`.
   - Create the object centered in the **current viewport** (`screenToWorld` of the stage center), scaled to a sane max (e.g. fit within ~600 world px), push to `objects`, `redraw()`, `emitAction('image', obj)`, `scheduleStateSave()`.

4. **Upload flow (PDF):** load **pdf.js** (CDN `<script>` in `whiteboard.html`, like the existing socket.io CDN tag). For each page: `getViewport({scale: 2})` → render to an offscreen canvas → `canvas.toBlob('image/png')` → upload via the same route → place pages **stacked vertically** (offset each by the previous page height + gap) starting at the viewport center. Emit one `image` action per page.

5. **Remote sync:** add an `'image'` case to `applyRemoteAction` (dedupe by `id`, ensure URL enters `imageCache`, `redraw()`). The existing generic stroke/shape/text branch is the template.

---

## Part 4 — Backend: upload route

**File: `app/routes/whiteboard_routes.py`** — add:

```
POST /api/whiteboards/<code>/upload   (multipart, field "file")
```
- Auth: `session.get('user_id')` (mirror the other routes here).
- Membership: reuse `WhiteboardController.get_board_for_user(user_id, code)` (or the access check used by `controller.get_state`) → 403/404 on failure.
- Validate + save reusing the **existing chat-upload pattern** in `app/sockets.py:249-271`:
  - extension whitelist — reuse/trim `ALLOWED_SHARED_FILE_EXTENSIONS` from `app/routes/home.py` to image types (PDFs arrive pre-rasterized as PNG, so the server only needs images);
  - `secure_filename` + `uuid.uuid4().hex` stored name;
  - save to `os.path.join(current_app.root_path, 'static', 'uploads', 'whiteboard')` (`makedirs(exist_ok=True)`);
  - enforce the 25 MB cap (`MAX_SHARED_FILE_SIZE`, `app/routes/home.py:37`).
- Response: `{'status':'success','url': url_for('static', filename='uploads/whiteboard/<stored>'), 'width':..., 'height':...}`. Files are served by Flask's built-in `/static/...` — **no DB table needed** (unlike chat `shared_file`); the URL lives only in board state.

**File: `app/__init__.py`** — bump the Socket.IO buffer so large persisted-state saves don't get cut at the 1 MB default:
```py
socketio = SocketIO(async_mode='threading', max_http_buffer_size=10_000_000)
```
(Image bytes never travel over the socket — only URLs — but boards with many objects make the `whiteboard_save_state` JSON grow.)

No DB schema change: image objects are part of the existing `whiteboard_state.state` LONGTEXT JSON.

---

## Critical files

| File | Change |
|------|--------|
| `app/static/js/whiteboard.js` | viewport + world coords, redraw/transform refactor, in-progress-object drawing, pan/zoom/Hand/space, image object type + cache, upload + pdf.js, remote `image` action |
| `app/templates/whiteboard.html` | Hand tool btn, Upload btn + hidden file input, zoom-control panel, pdf.js CDN `<script>` |
| `app/static/css/whiteboard.css` | zoom controls, hand/grab cursors, upload button, (image selection handles if stretch) |
| `app/routes/whiteboard_routes.py` | new `POST .../upload` multipart route |
| `app/__init__.py` | `max_http_buffer_size` |

Reused as-is: `secure_filename` + `uuid` + `upload_dir` pattern (`app/sockets.py:249-271`), `ALLOWED_SHARED_FILE_EXTENSIONS` / `MAX_SHARED_FILE_SIZE` (`app/routes/home.py`), `WhiteboardController.get_board_for_user`, the `emitAction`/`applyRemoteAction`/`scheduleStateSave` sync pipeline.

---

## Verification

1. Run `python run.py`; open `/whiteboard/<code>` in **two** browser profiles on the same code.
2. **Infinite canvas:** draw, then wheel-pan far away and back — strokes persist at world positions. Ctrl/⌘+wheel zooms toward the cursor; zoom buttons + reset work; Hand tool and spacebar-drag pan.
3. **Backward compat:** open a board that already had content (pre-change state) — it renders unchanged at 100%.
4. **Image upload:** add a PNG/JPG — appears at the viewport center in **both** browsers; Move repositions it; Delete removes it; reload restores it (persisted state).
5. **PDF upload:** add a multi-page PDF — each page lands as a stacked image in both clients.
6. **Coordinate integrity:** zoom in, drop an image, switch to Move — selection outline and hit-testing line up with the image at any zoom; eraser ring matches stroke width on screen.
7. **Persistence/limits:** large board with several images + many strokes reloads correctly (confirms state save under the raised socket buffer).
