from __future__ import annotations

import pandas as pd

from app.config import ensure_directories, raw_dataset_path
from app.utils import normalize_text


LOCATION_STORIES = [
    'near the library help desk after an evening study session',
    'outside the canteen during lunch break',
    'in the electronics lab after class',
    'inside classroom B-204 after a lecture',
    'around the bus parking area before leaving campus',
    'near the auditorium entrance during an event',
]


CATEGORY_STYLE = {
    'Headphones': 'over-ear audio accessory',
    'Earbuds': 'small wireless audio accessory',
    'Wallet': 'compact personal item',
    'Bottle': 'daily-use drink container',
    'Backpack': 'student carry bag',
    'E-reader': 'flat reading device',
    'Watch': 'wrist accessory',
    'Mouse': 'computer accessory',
    'Speaker': 'portable audio device',
    'Bag': 'carry bag',
    'Pen': 'metal writing instrument',
}


def synthesize_description(row: pd.Series, index: int) -> str:
    category = normalize_text(row.get('category'))
    color = normalize_text(row.get('color')).lower()
    brand = normalize_text(row.get('brand'))
    title = normalize_text(row.get('title'))
    notes = normalize_text(row.get('notes'))
    hint = LOCATION_STORIES[index % len(LOCATION_STORIES)]
    style = CATEGORY_STYLE.get(category, category.lower())

    return (
        f"Lost a {color} {style} from {brand}. "
        f"It resembles {title} and was likely misplaced {hint}. "
        f"Distinct note: {notes}."
    )


def main() -> None:
    ensure_directories()
    path = raw_dataset_path()
    if not path.exists():
        raise FileNotFoundError(f'Raw dataset not found: {path}')

    df = pd.read_csv(path)
    df['lost_description'] = [synthesize_description(row, idx) for idx, (_, row) in enumerate(df.iterrows())]
    if 'location_hint' not in df.columns:
        df['location_hint'] = [LOCATION_STORIES[idx % len(LOCATION_STORIES)] for idx in range(len(df))]
    if 'notes' not in df.columns:
        df['notes'] = ''

    df.to_csv(path, index=False)
    print(f'Updated {path} with more realistic lost-item descriptions.')


if __name__ == '__main__':
    main()
