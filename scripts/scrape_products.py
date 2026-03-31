from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.config import DEFAULT_SAMPLE_SIZE, ensure_directories, raw_dataset_path
from app.utils import normalize_text


BASE_PRODUCTS = [
    ('AirPods Max', 'Headphones', 'Apple', 'Gold', 'Premium over-ear wireless headphones with smart case.'),
    ('Classic Leather Wallet', 'Wallet', 'Fossil', 'Brown', 'Slim leather wallet with card slots and ID window.'),
    ('Hydro Flask 32oz', 'Bottle', 'Hydro Flask', 'Black', 'Insulated stainless steel water bottle for daily use.'),
    ('Kindle Paperwhite', 'E-reader', 'Amazon', 'Black', 'Lightweight e-reader with glare-free display.'),
    ('Nike Everyday Backpack', 'Backpack', 'Nike', 'Black', 'Campus backpack with padded shoulder straps and laptop sleeve.'),
    ('Casio Vintage Watch', 'Watch', 'Casio', 'Silver', 'Retro digital watch with stainless steel band.'),
    ('Logitech MX Master 3S', 'Mouse', 'Logitech', 'Graphite', 'Ergonomic wireless mouse for productivity.'),
    ('Sony WH-1000XM5', 'Headphones', 'Sony', 'Black', 'Noise-canceling wireless headphones with carrying case.'),
    ('JBL Flip 6', 'Speaker', 'JBL', 'Blue', 'Portable Bluetooth speaker with waterproof body.'),
    ('Adidas Duffel Bag', 'Bag', 'Adidas', 'Navy', 'Medium-size sports duffel with side compartments.'),
    ('Parker Metal Pen', 'Pen', 'Parker', 'Silver', 'Refillable signature pen with smooth grip.'),
    ('Samsung Galaxy Buds 2', 'Earbuds', 'Samsung', 'White', 'Compact wireless earbuds with charging case.'),
]

LOCATIONS = ['library', 'canteen', 'lab', 'classroom', 'bus stop', 'auditorium']
NOTES = ['slight scratch on side', 'with student ID sticker', 'kept in a leather case', 'has initials on it', 'inside front pocket', 'charger missing']


def build_records(sample_size: int) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for index in range(sample_size):
        title, category, brand, color, description = BASE_PRODUCTS[index % len(BASE_PRODUCTS)]
        slug = title.lower().replace(' ', '_').replace('-', '_')
        records.append(
            {
                'title': title,
                'category': category,
                'brand': brand,
                'color': color,
                'description': description,
                'image_path': f'data/raw/images/{slug}.jpg',
                'price': 35 + (index % 8) * 22,
                'source_url': f'https://example.com/{slug}',
                'location_hint': LOCATIONS[index % len(LOCATIONS)],
                'notes': NOTES[index % len(NOTES)],
            }
        )
    return records


def main() -> None:
    ensure_directories()
    output_path = raw_dataset_path()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(build_records(DEFAULT_SAMPLE_SIZE))
    df['title'] = df['title'].apply(normalize_text)
    df.to_csv(output_path, index=False)

    print(f'Wrote sample scraped dataset with {len(df)} rows to {output_path}')
    print('For submission, replace build_records() with a real scraper or API ingestion step.')


if __name__ == '__main__':
    main()
