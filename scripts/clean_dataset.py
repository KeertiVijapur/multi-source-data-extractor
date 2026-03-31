from __future__ import annotations

import pandas as pd

from app.config import ensure_directories, processed_dataset_path, raw_dataset_path
from app.utils import build_search_text, clean_price, dedupe_records, normalize_text, resolve_image_path


REQUIRED_COLUMNS = [
    'item_id',
    'title',
    'category',
    'brand',
    'color',
    'description',
    'lost_description',
    'image_path',
    'price',
    'source_url',
    'location_hint',
    'notes',
]


def main() -> None:
    ensure_directories()

    input_path = raw_dataset_path()
    if not input_path.exists():
        raise FileNotFoundError(f'Raw dataset not found: {input_path}')

    df = pd.read_csv(input_path)

    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            df[column] = ''

    text_columns = ['title', 'category', 'brand', 'color', 'description', 'lost_description', 'source_url', 'location_hint', 'notes']
    for column in text_columns:
        df[column] = df[column].apply(normalize_text)

    df['price'] = df['price'].apply(clean_price)
    df['category'] = df['category'].replace({'E-reader': 'Ereader'})
    df['image_path'] = df['image_path'].apply(resolve_image_path)
    df = dedupe_records(df, ['title', 'brand', 'color', 'notes'])
    df = df[df['title'] != ''].copy()
    df['item_id'] = range(1001, 1001 + len(df))
    df['search_text'] = df.apply(build_search_text, axis=1)
    df = df.sort_values(['category', 'brand', 'title']).reset_index(drop=True)

    output_path = processed_dataset_path()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f'Wrote cleaned dataset with {len(df)} rows to {output_path}')
    print(f"Categories: {', '.join(sorted(df['category'].dropna().unique()))}")


if __name__ == '__main__':
    main()
