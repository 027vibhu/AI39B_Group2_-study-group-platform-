import json
import re

# Reuse the PDF reading + NVIDIA client plumbing already used for flashcards.
from app.services.flashcard_ai import (
    extract_pdf_text,
    _render_pdf_to_images,
    _complete,
)

SUMMARY_INSTRUCTION = (
    'Summarize the study material for a student revising it. '
    'Return ONLY a JSON object with two keys: '
    '"overview" (a 2-3 sentence plain-language summary string) and '
    '"key_points" (an array of 4-8 concise bullet strings covering the most '
    'important concepts, in the order they appear). '
    'Do not include any text outside the JSON object.'
)


def _parse_summary(content):
    content = content.strip()
    content = re.sub(r'^```(?:json)?', '', content).strip()
    content = re.sub(r'```$', '', content).strip()

    match = re.search(r'\{.*\}', content, re.DOTALL)
    raw = match.group(0) if match else content
    data = json.loads(raw)

    overview = (data.get('overview') or '').strip()
    key_points = []
    for point in data.get('key_points') or []:
        point = (str(point) or '').strip()
        if point:
            key_points.append(point[:400])

    if not overview and not key_points:
        raise ValueError('The model did not return a usable summary. Please try again.')

    return {'overview': overview, 'key_points': key_points}


def _summarize_text(text):
    messages = [
        {'role': 'system', 'content': 'You are a study assistant that writes clear, accurate summaries.'},
        {'role': 'user', 'content': f"{SUMMARY_INSTRUCTION}\n\nSTUDY MATERIAL:\n{text}"},
    ]
    return _parse_summary(_complete(messages))


def _summarize_images(images_b64):
    content = [
        {
            'type': 'text',
            'text': (
                SUMMARY_INSTRUCTION
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
    return _parse_summary(_complete(messages))


def generate_summary_from_pdf(pdf_path):
    """Generate a summary from a PDF.

    Uses embedded text when present; otherwise sends rendered page images to
    the multimodal model. Returns a dict with "overview" (str) and
    "key_points" (list[str]). Raises ValueError for unusable input/output and
    RuntimeError for missing configuration.
    """
    text = extract_pdf_text(pdf_path)
    if text:
        return _summarize_text(text)

    images = _render_pdf_to_images(pdf_path)
    if not images:
        raise ValueError('Could not read this PDF — it has no text and no rasterizable pages.')
    return _summarize_images(images)
