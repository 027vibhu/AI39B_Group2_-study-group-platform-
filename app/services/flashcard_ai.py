import base64
import json
import re

from config import Config

MAX_CHARS = 12000
MAX_VISION_PAGES = 5
MAX_IMAGE_BYTES = 140_000


def extract_pdf_text(pdf_path, max_chars=MAX_CHARS):
    try:
        import pdfplumber
    except ImportError:
        raise RuntimeError('pdfplumber is not installed. Run: pip install pdfplumber')

    parts = []
    total = 0
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ''
            if not text:
                continue
            parts.append(text)
            total += len(text)
            if total >= max_chars:
                break
    return '\n\n'.join(parts).strip()[:max_chars]


def _render_pdf_to_images(pdf_path, max_pages=MAX_VISION_PAGES, max_bytes=MAX_IMAGE_BYTES):
    """Render the first `max_pages` pages to base64 JPEGs, downscaling each
    page until it fits under the API's inline-image size limit."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise RuntimeError('pymupdf is not installed. Run: pip install pymupdf')

    images = []
    doc = fitz.open(pdf_path)
    try:
        for index, page in enumerate(doc):
            if index >= max_pages:
                break
            data = None
            for scale in (2.0, 1.5, 1.0, 0.75):
                pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
                data = pix.tobytes(output='jpg', jpg_quality=70)
                if len(data) <= max_bytes:
                    break
            if data:
                images.append(base64.b64encode(data).decode('ascii'))
    finally:
        doc.close()
    return images


def _build_client():
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError('openai is not installed. Run: pip install openai')

    if not Config.NVIDIA_API_KEY:
        raise RuntimeError('NVIDIA_API_KEY is not configured in .env.')
    return OpenAI(api_key=Config.NVIDIA_API_KEY, base_url=Config.NVIDIA_BASE_URL)


def _complete(messages, max_tokens=4096):
    client = _build_client()
    response = client.chat.completions.create(
        model=Config.NVIDIA_MODEL,
        messages=messages,
        temperature=0.4,
        max_tokens=max_tokens,
        extra_body={'chat_template_kwargs': {'enable_thinking': False}},
    )
    return response.choices[0].message.content or ''


def _card_instruction(count):
    return (
        f"Create {count} study flashcards from the study material. "
        'Return ONLY a JSON array of objects, each with "question" and "answer" keys. '
        'Questions must be concise; answers must be accurate and self-contained. '
        'Do not include any text outside the JSON array.'
    )


def _parse_cards(content):
    content = content.strip()
    content = re.sub(r'^```(?:json)?', '', content).strip()
    content = re.sub(r'```$', '', content).strip()

    match = re.search(r'\[.*\]', content, re.DOTALL)
    raw = match.group(0) if match else content
    data = json.loads(raw)

    cards = []
    for item in data:
        if not isinstance(item, dict):
            continue
        question = (item.get('question') or '').strip()
        answer = (item.get('answer') or '').strip()
        if question and answer:
            cards.append((question[:500], answer))
    return cards


def _generate_cards_from_text(text, count=10):
    messages = [
        {'role': 'system', 'content': 'You are a study assistant that writes high-quality flashcards.'},
        {'role': 'user', 'content': f"{_card_instruction(count)}\n\nSTUDY MATERIAL:\n{text}"},
    ]
    return _parse_cards(_complete(messages))


def _generate_cards_from_images(images_b64, count=10):
    content = [
        {
            'type': 'text',
            'text': (
                _card_instruction(count)
                + ' The study material is in the attached image(s) of handwritten or '
                'scanned notes; read them carefully, including any handwriting.'
            ),
        }
    ]
    for image_b64 in images_b64:
        content.append({
            'type': 'image_url',
            'image_url': {'url': f'data:image/jpeg;base64,{image_b64}'},
        })
    messages = [{'role': 'user', 'content': content}]
    return _parse_cards(_complete(messages))


def generate_cards_from_pdf(pdf_path, count=10):
    """Generate Q/A flashcards from a PDF.

    Uses embedded text when present; otherwise sends rendered page images
    directly to the multimodal model. Returns a list of (question, answer)
    tuples. Raises ValueError for unusable input/output and RuntimeError for
    missing configuration.
    """
    text = extract_pdf_text(pdf_path)
    if text:
        cards = _generate_cards_from_text(text, count)
    else:
        images = _render_pdf_to_images(pdf_path)
        if not images:
            raise ValueError('Could not read this PDF — it has no text and no rasterizable pages.')
        cards = _generate_cards_from_images(images, count)

    if not cards:
        raise ValueError('The model did not return usable flashcards. Please try again.')
    return cards
