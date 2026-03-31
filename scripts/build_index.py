from __future__ import annotations

from pathlib import Path

import chromadb
import pandas as pd
import torch
from PIL import Image
from sentence_transformers import SentenceTransformer
from transformers import CLIPModel, CLIPProcessor

from app.config import CHROMA_DIR, CLIP_MODEL_NAME, TEXT_MODEL_NAME, ensure_directories, processed_dataset_path
from app.utils import build_search_text


TEXT_COLLECTION_NAME = 'lost_found_text'
IMAGE_COLLECTION_NAME = 'lost_found_image'


def build_text_embeddings(df: pd.DataFrame, collection, text_model: SentenceTransformer) -> None:
    search_texts = df.apply(build_search_text, axis=1).tolist()
    embeddings = text_model.encode(search_texts, convert_to_numpy=True)

    collection.upsert(
        ids=df['item_id'].astype(str).tolist(),
        embeddings=embeddings.tolist(),
        documents=df['search_text'].fillna('').tolist(),
        metadatas=[
            {
                'title': str(row.get('title', '')),
                'category': str(row.get('category', '')),
                'brand': str(row.get('brand', '')),
                'color': str(row.get('color', '')),
                'image_path': str(row.get('image_path', '')),
                'price': str(row.get('price', '')),
                'description': str(row.get('description', '')),
                'lost_description': str(row.get('lost_description', '')),
                'location_hint': str(row.get('location_hint', '')),
                'notes': str(row.get('notes', '')),
            }
            for _, row in df.iterrows()
        ],
    )


def extract_image_features(clip_model: CLIPModel, inputs: dict[str, torch.Tensor]) -> torch.Tensor:
    with torch.no_grad():
        features = clip_model.get_image_features(**inputs)
        if hasattr(features, 'pooler_output'):
            features = features.pooler_output
        elif hasattr(features, 'last_hidden_state'):
            features = features.last_hidden_state[:, 0, :]
        features = features / features.norm(dim=-1, keepdim=True)
    return features


def build_image_embeddings(df: pd.DataFrame, collection, clip_model: CLIPModel, clip_processor: CLIPProcessor) -> None:
    ids: list[str] = []
    embeddings: list[list[float]] = []
    metadatas: list[dict[str, str]] = []
    documents: list[str] = []

    for _, row in df.iterrows():
        image_path = Path(str(row.get('image_path', '')))
        if not image_path.exists():
            continue

        image = Image.open(image_path).convert('RGB')
        inputs = clip_processor(images=image, return_tensors='pt')
        features = extract_image_features(clip_model, inputs)

        ids.append(str(row['item_id']))
        embeddings.append(features[0].cpu().tolist())
        documents.append(str(row.get('search_text', '')))
        metadatas.append(
            {
                'title': str(row.get('title', '')),
                'category': str(row.get('category', '')),
                'brand': str(row.get('brand', '')),
                'color': str(row.get('color', '')),
                'image_path': str(image_path),
                'lost_description': str(row.get('lost_description', '')),
            }
        )

    if ids:
        collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)


def reset_collection(client, name: str):
    try:
        client.delete_collection(name)
    except Exception:
        pass
    return client.get_or_create_collection(name)


def main() -> None:
    ensure_directories()
    dataset_path = processed_dataset_path()
    if not dataset_path.exists():
        raise FileNotFoundError(f'Processed dataset not found: {dataset_path}')

    df = pd.read_csv(dataset_path)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    text_collection = reset_collection(client, TEXT_COLLECTION_NAME)
    image_collection = reset_collection(client, IMAGE_COLLECTION_NAME)

    text_model = SentenceTransformer(TEXT_MODEL_NAME)
    clip_model = CLIPModel.from_pretrained(CLIP_MODEL_NAME)
    clip_processor = CLIPProcessor.from_pretrained(CLIP_MODEL_NAME)

    build_text_embeddings(df, text_collection, text_model)
    build_image_embeddings(df, image_collection, clip_model, clip_processor)

    print(f'Indexed {len(df)} records into ChromaDB at {CHROMA_DIR}')


if __name__ == '__main__':
    main()