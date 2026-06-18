"""
Backend route for "Generate Flashcards" — drop this into your existing
`home` blueprint (the same one that has upload_note / share_note / delete_note).
 
Install the two new dependencies:
    pip install pypdf anthropic
 
Set your API key in the environment before running the app:
    export ANTHROPIC_API_KEY="sk-ant-..."
 
Wire-up notes:
- The frontend (notes.html) calls this route via:
    url_for('home.generate_flashcards', note_id=note.id)
  with a POST request, and expects back JSON shaped like:
    { "flashcards": [ { "question": "...", "answer": "..." }, ... ] }
- This example assumes a `Note` model with `id`, `user_id`, and `pdf_url`
  (the same relative path used in `url_for('static', filename=note.pdf_url)`),
  matching what's already in your notes.html template. Adjust the import
  and field names to match your actual models.py.
- If you use Flask-WTF's CSRFProtect, either exempt this route or have the
  frontend send the token in an `X-CSRFToken` header.
"""
 
import os
import json
import re
 
from flask import current_app, jsonify, abort
from flask_login import login_required, current_user
from pypdf import PdfReader
import anthropic
 
# from .models import Note          # <- adjust to your actual import
# from . import home_bp as home     # <- adjust to your actual blueprint name
 
MAX_CHARS_TO_MODEL = 15000   # keeps prompt size (and cost) bounded
MIN_CARDS = 8
MAX_CARDS = 15
 
 
def _extract_pdf_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    text = "\n".join(pages).strip()
    return text[:MAX_CHARS_TO_MODEL]
 
 
def _build_prompt(note_title: str, text: str) -> str:
    return f"""You are creating study flashcards from a student's notes.
 
Note title: "{note_title}"
 
Notes content:
\"\"\"
{text}
\"\"\"
 
Create between {MIN_CARDS} and {MAX_CARDS} flashcards that cover the key
concepts, definitions, and facts in this content. Each flashcard should
have a clear, specific question on the front and a concise, accurate
answer on the back (1-3 sentences).
 
Respond with ONLY a JSON array, no preamble, no markdown code fences, in
exactly this shape:
[
  {{"question": "...", "answer": "..."}},
  {{"question": "...", "answer": "..."}}
]
"""
 
 
def _parse_flashcards_json(raw: str):
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    data = json.loads(cleaned)
 
    flashcards = []
    for item in data:
        question = (item.get("question") or "").strip()
        answer = (item.get("answer") or "").strip()
        if question and answer:
            flashcards.append({"question": question, "answer": answer})
    return flashcards
 
 
# @home.route('/notes/<int:note_id>/flashcards', methods=['POST'])
# @login_required
def generate_flashcards(note_id):
    note = Note.query.get_or_404(note_id)
 
    # Ownership check — don't let users generate flashcards from notes
    # that aren't theirs (including ones merely shared with them, unless
    # you want to allow that).
    if note.user_id != current_user.id:
        abort(403)
 
    pdf_path = os.path.join(current_app.static_folder, note.pdf_url)
    if not os.path.exists(pdf_path):
        return jsonify({"error": "PDF file not found"}), 404
 
    try:
        text = _extract_pdf_text(pdf_path)
    except Exception:
        current_app.logger.exception("Failed to extract PDF text for note %s", note_id)
        return jsonify({"error": "Could not read this PDF"}), 400
 
    if not text:
        return jsonify({"error": "This PDF doesn't contain extractable text"}), 400
 
    try:
        client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": _build_prompt(note.title, text)}],
        )
        raw_text = "".join(
            block.text for block in response.content if block.type == "text"
        )
        flashcards = _parse_flashcards_json(raw_text)
    except Exception:
        current_app.logger.exception("Flashcard generation failed for note %s", note_id)
        return jsonify({"error": "Flashcard generation failed"}), 502
 
    if not flashcards:
        return jsonify({"error": "No flashcards could be generated"}), 502
 
    return jsonify({"flashcards": flashcards})
