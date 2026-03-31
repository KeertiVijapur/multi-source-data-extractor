from __future__ import annotations

import time

import pandas as pd
import requests

from app.config import RAW_IMAGES_DIR, ensure_directories


IMAGE_MANIFEST = {
    'airpods_max.jpg': {
        'url': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Headphones%20(56330).jpg',
        'license': 'CC0 via Wikimedia Commons',
        'source_page': 'https://commons.wikimedia.org/wiki/File:Headphones_(56330).jpg',
    },
    'classic_leather_wallet.jpg': {
        'url': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Cub%20Men%27s%20Wallet.jpg',
        'license': 'CC-BY-SA-4.0 via Wikimedia Commons',
        'source_page': 'https://commons.wikimedia.org/wiki/File:Cub_Men%27s_Wallet.jpg',
    },
    'hydro_flask_32oz.jpg': {
        'url': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Water%20bottle%20(13779).jpg',
        'license': 'CC-BY-SA-4.0 via Wikimedia Commons',
        'source_page': 'https://commons.wikimedia.org/wiki/File:Water_bottle_(13779).jpg',
    },
    'kindle_paperwhite.jpg': {
        'url': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Tablet%20Computer.jpg',
        'license': 'Licensed on Wikimedia Commons',
        'source_page': 'https://commons.wikimedia.org/wiki/File:Tablet_Computer.jpg',
    },
    'nike_everyday_backpack.jpg': {
        'url': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/School%20bag%20backpack.jpg',
        'license': 'CC-BY-SA-3.0 via Wikimedia Commons',
        'source_page': 'https://commons.wikimedia.org/wiki/File:School_bag_backpack.jpg',
    },
    'casio_vintage_watch.jpg': {
        'url': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Wrist%20Watch.jpg',
        'license': 'CC-BY-SA-4.0 via Wikimedia Commons',
        'source_page': 'https://commons.wikimedia.org/wiki/File:Wrist_Watch.jpg',
    },
    'logitech_mx_master_3s.jpg': {
        'url': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Computer%20mice.jpg',
        'license': 'CC0 via Wikimedia Commons',
        'source_page': 'https://commons.wikimedia.org/wiki/File:Computer_mice.jpg',
    },
    'sony_wh_1000xm5.jpg': {
        'url': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Headphones.jpg',
        'license': 'CC-BY-SA-3.0 via Wikimedia Commons',
        'source_page': 'https://commons.wikimedia.org/wiki/File:Headphones.jpg',
    },
    'jbl_flip_6.jpg': {
        'url': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Speakers.jpg',
        'license': 'CC-BY-SA-4.0 via Wikimedia Commons',
        'source_page': 'https://commons.wikimedia.org/wiki/File:Speakers.jpg',
    },
    'adidas_duffel_bag.jpg': {
        'url': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/The%20North%20Face%20Base%20Camp%20duffel%20bag%20(48585042386).jpg',
        'license': 'CC-BY-2.0 via Wikimedia Commons',
        'source_page': 'https://commons.wikimedia.org/wiki/File:The_North_Face_Base_Camp_duffel_bag_(48585042386).jpg',
    },
    'parker_metal_pen.jpg': {
        'url': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Pen.jpg',
        'license': 'Public domain via Wikimedia Commons',
        'source_page': 'https://commons.wikimedia.org/wiki/File:Pen.jpg',
    },
    'samsung_galaxy_buds_2.jpg': {
        'url': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Earphones.jpg',
        'license': 'CC-BY-SA-4.0 via Wikimedia Commons',
        'source_page': 'https://commons.wikimedia.org/wiki/File:Earphones.jpg',
    },
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
}


def fetch_with_retry(session: requests.Session, url: str, retries: int = 3) -> requests.Response:
    wait_seconds = 2
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()
            return response
        except Exception as exc:
            last_error = exc
            time.sleep(wait_seconds)
            wait_seconds *= 2
    raise last_error  # type: ignore[misc]


def main() -> None:
    ensure_directories()
    RAW_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    session = requests.Session()
    session.headers.update(HEADERS)

    for file_name, item in IMAGE_MANIFEST.items():
        target = RAW_IMAGES_DIR / file_name
        if target.exists() and target.stat().st_size > 0:
            print(f'Skipped existing {file_name}')
            rows.append(
                {
                    'file_name': file_name,
                    'local_path': str(target),
                    'resolved_url': '',
                    'source_url': item['source_page'],
                    'download_url': item['url'],
                    'license': item['license'],
                }
            )
            continue

        try:
            response = fetch_with_retry(session, item['url'])
            target.write_bytes(response.content)
            rows.append(
                {
                    'file_name': file_name,
                    'local_path': str(target),
                    'resolved_url': response.url,
                    'source_url': item['source_page'],
                    'download_url': item['url'],
                    'license': item['license'],
                }
            )
            print(f'Downloaded {file_name}')
            time.sleep(2)
        except Exception as exc:
            print(f'Failed {file_name}: {exc}')

    manifest_path = RAW_IMAGES_DIR / 'image_sources.csv'
    pd.DataFrame(rows).to_csv(manifest_path, index=False)
    print(f'Wrote image source manifest to {manifest_path}')


if __name__ == '__main__':
    main()
