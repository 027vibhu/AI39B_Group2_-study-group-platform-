"""Conversational Q&A over a note's PDF.

The NVIDIA build API is a stateless chat-completions endpoint, so the document
context must travel with every request. To avoid re-parsing the PDF each turn,
the extracted text is cached on the note (see Note.set_content_text) and passed
in here as `content_text`. Conversation history is supplied by the caller (the
browser keeps it and sends recent turns), keeping the server stateless.
"""

# Reuse the PDF rendering + NVIDIA client plumbing already used for flashcards.
from app.services.flashcard_ai import _complete, _render_pdf_to_images

MAX_HISTORY_TURNS = 8          # cap conversation context sent to the model
MAX_HISTORY_CHARS = 1500       # cap each historical message length
MAX_QUESTION_CHARS = 2000      # cap a single user question

CHAT_SYSTEM = (
    'You are a study assistant helping a student understand a document. '
    'Answer questions using ONLY the study material provided below. '
    'If the answer is not in the material, say so plainly instead of guessing. '
    'Give a complete, well-explained answer: state the answer, then explain the '
    'reasoning and any relevant detail or examples from the material so the '
    'student actually understands it. Aim for at least a few sentences (use '
    'short paragraphs or bullet points when helpful); never reply with just a '
    'word or two.'
)


def _sanitize_history(history):
    """Coerce caller-supplied history into trusted {role, content} messages."""
    if not isinstance(history, list):
        return []
    clean = []
    for item in history:
        if not isinstance(item, dict):
            continue
        role = item.get('role')
        if role not in ('user', 'assistant'):
            continue
        content = (item.get('content') or '').strip()
        if not content:
            continue
        clean.append({'role': role, 'content': content[:MAX_HISTORY_CHARS]})
    return clean[-MAX_HISTORY_TURNS:]


def chat_with_note(content_text, question, history=None, images_b64=None):
    """Answer a question about a note.

    `content_text` is the cached extracted PDF text (preferred). When the PDF
    has no embedded text, pass `images_b64` (rendered pages) instead and the
    question is answered in multimodal mode. Returns the assistant's reply as a
    string. Raises ValueError for unusable input and RuntimeError for missing
    configuration.
    """
    question = (question or '').strip()
    if not question:
        raise ValueError('Please enter a question.')
    question = question[:MAX_QUESTION_CHARS]

    messages = [{'role': 'system', 'content': CHAT_SYSTEM}]

    if content_text:
        messages[0]['content'] += f"\n\nSTUDY MATERIAL:\n{content_text}"
        messages.extend(_sanitize_history(history))
        messages.append({'role': 'user', 'content': question})
    elif images_b64:
        # No embedded text: send rendered pages alongside the question.
        messages[0]['content'] += (
            ' The study material is in the attached image(s) of scanned or '
            'handwritten notes; read them carefully, including any handwriting.'
        )
        messages.extend(_sanitize_history(history))
        content = [{'type': 'text', 'text': question}]
        for image_b64 in images_b64:
            content.append({
                'type': 'image_url',
                'image_url': {'url': f'data:image/jpeg;base64,{image_b64}'},
            })
        messages.append({'role': 'user', 'content': content})
    else:
        raise ValueError('Could not read this PDF — it has no usable text or pages.')

    reply = _complete(messages, max_tokens=1024).strip()
    if not reply:
        raise ValueError('The model did not return an answer. Please try again.')
    return reply


def render_pdf_images(pdf_path):
    """Render a PDF's pages to base64 JPEGs for the no-embedded-text fallback."""
    return _render_pdf_to_images(pdf_path)
