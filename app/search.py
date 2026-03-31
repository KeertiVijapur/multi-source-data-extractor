from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import chromadb
import torch
from PIL import Image
from sentence_transformers import SentenceTransformer
from transformers import CLIPModel, CLIPProcessor

from app.config import CHROMA_DIR, CLIP_MODEL_NAME, DEFAULT_TEXT_WEIGHT, TEXT_MODEL_NAME
from app.utils import lexical_overlap_score


@dataclass
class SearchBundle:
    text_collection: Any
    image_collection: Any
    text_model: SentenceTransformer
    clip_model: CLIPModel
    clip_processor: CLIPProcessor


_bundle: SearchBundle | None = None


def get_bundle() -> SearchBundle:
    global _bundle
    if _bundle is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _bundle = SearchBundle(
            text_collection=client.get_or_create_collection('lost_found_text'),
            image_collection=client.get_or_create_collection('lost_found_image'),
            text_model=SentenceTransformer(TEXT_MODEL_NAME),
            clip_model=CLIPModel.from_pretrained(CLIP_MODEL_NAME),
            clip_processor=CLIPProcessor.from_pretrained(CLIP_MODEL_NAME),
        )
    return _bundle


def search_by_text(query: str, top_k: int = 5) -> dict[str, Any] | None:
    query = query.strip()
    if not query:
        return None
    bundle = get_bundle()
    embedding = bundle.text_model.encode([query], convert_to_numpy=True)[0].tolist()
    return bundle.text_collection.query(query_embeddings=[embedding], n_results=top_k)


def extract_image_features(clip_model: CLIPModel, inputs: dict[str, torch.Tensor]) -> torch.Tensor:
    with torch.no_grad():
        features = clip_model.get_image_features(**inputs)
        if hasattr(features, 'pooler_output'):
            features = features.pooler_output
        elif hasattr(features, 'last_hidden_state'):
            features = features.last_hidden_state[:, 0, :]
        features = features / features.norm(dim=-1, keepdim=True)
    return features


def search_by_image(image_path: str | Path, top_k: int = 5) -> dict[str, Any] | None:
    bundle = get_bundle()
    image = Image.open(image_path).convert('RGB')
    inputs = bundle.clip_processor(images=image, return_tensors='pt')
    features = extract_image_features(bundle.clip_model, inputs)
    return bundle.image_collection.query(query_embeddings=[features[0].cpu().tolist()], n_results=top_k)


def fuse_results(
    text_results: dict[str, Any] | None,
    image_results: dict[str, Any] | None,
    query_text: str = '',
    text_weight: float = DEFAULT_TEXT_WEIGHT,
) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}

    def absorb(results: dict[str, Any], weight: float, source: str) -> None:
        ids = results.get('ids', [[]])[0]
        distances = results.get('distances', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]
        documents = results.get('documents', [[]])[0] if results.get('documents') else [''] * len(ids)

        for item_id, distance, metadata, document in zip(ids, distances, metadatas, documents):
            vector_score = 1.0 / (1.0 + float(distance))
            lexical = lexical_overlap_score(query_text, document or ' '.join(str(v) for v in (metadata or {}).values())) if query_text else 0.0
            score = (weight * vector_score) + (0.15 * lexical if source == 'text' else 0.0)

            if item_id not in merged:
                merged[item_id] = {
                    'item_id': item_id,
                    'score': 0.0,
                    'vector_score': vector_score,
                    'lexical_score': lexical,
                    'distance': distance,
                    'metadata': metadata or {},
                    'document': document,
                    'sources': set(),
                }
            merged[item_id]['score'] += score
            merged[item_id]['distance'] = min(float(merged[item_id]['distance']), float(distance))
            merged[item_id]['vector_score'] = max(float(merged[item_id]['vector_score']), vector_score)
            merged[item_id]['lexical_score'] = max(float(merged[item_id]['lexical_score']), lexical)
            merged[item_id]['sources'].add(source)
            if document and not merged[item_id]['document']:
                merged[item_id]['document'] = document

    if text_results:
        absorb(text_results, text_weight, 'text')
    if image_results:
        absorb(image_results, 1.0 - text_weight, 'image')

    ranked = sorted(merged.values(), key=lambda item: item['score'], reverse=True)
    for item in ranked:
        item['sources'] = ', '.join(sorted(item['sources']))
    return ranked
