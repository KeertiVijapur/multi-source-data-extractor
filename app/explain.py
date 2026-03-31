from __future__ import annotations

from typing import Any

import requests

from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from app.utils import confidence_from_distance, lexical_overlap_score


def build_rule_based_explanation(query_text: str, metadata: dict[str, Any], distance: float | None = None) -> str:
    query = query_text.lower().strip()
    reasons: list[str] = []

    title = str(metadata.get('title', ''))
    category = str(metadata.get('category', ''))
    brand = str(metadata.get('brand', ''))
    color = str(metadata.get('color', ''))
    candidate_text = ' '.join([title, category, brand, color, str(metadata.get('lost_description', ''))])

    if category and category.lower() in query:
        reasons.append(f"category matches '{category}'")
    if brand and brand.lower() in query:
        reasons.append(f"brand matches '{brand}'")
    if color and color.lower() in query:
        reasons.append(f"color matches '{color}'")

    lexical = lexical_overlap_score(query, candidate_text)
    if lexical >= 0.25:
        reasons.append('multiple descriptive terms overlap strongly')
    elif title and any(token in title.lower() for token in query.split() if len(token) > 3):
        reasons.append('the title is semantically close to the query')

    confidence = confidence_from_distance(distance)

    if not reasons:
        reasons.append('embedding similarity stayed high even with different wording')

    return f"Potential match because {', '.join(reasons)}. Confidence estimate: {confidence:.2f}."


def explain_with_ollama(query_text: str, metadata: dict[str, Any], distance: float | None = None) -> str:
    prompt = (
        'You are helping a student understand why a found item may match their lost item. '
        'Answer in 2 short sentences. Mention visual cues, category, brand, or semantic similarity if relevant.\n\n'
        f"User query: {query_text or 'image-based search only'}\n"
        f"Candidate title: {metadata.get('title', '')}\n"
        f"Category: {metadata.get('category', '')}\n"
        f"Brand: {metadata.get('brand', '')}\n"
        f"Color: {metadata.get('color', '')}\n"
        f"Description: {metadata.get('lost_description', '') or metadata.get('description', '')}\n"
        f"Distance: {distance}\n"
    )

    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            'model': OLLAMA_MODEL,
            'prompt': prompt,
            'stream': False,
        },
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    return str(payload.get('response', '')).strip()


def explain_match(
    query_text: str,
    metadata: dict[str, Any],
    distance: float | None = None,
    local_llm_mode: str = 'disabled',
) -> str:
    if local_llm_mode.lower() == 'ollama':
        try:
            answer = explain_with_ollama(query_text, metadata, distance)
            if answer:
                return answer
        except Exception:
            pass

    return build_rule_based_explanation(query_text, metadata, distance)
