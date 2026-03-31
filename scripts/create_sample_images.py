from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

from app.config import RAW_IMAGES_DIR, ensure_directories


IMAGE_SPECS = [
    ('airpods_max.jpg', '#F4D35E', '#2B2D42', 'AirPods Max', 'headphones'),
    ('classic_leather_wallet.jpg', '#8D6A4F', '#F8F4E3', 'Wallet', 'wallet'),
    ('hydro_flask_32oz.jpg', '#4F6D7A', '#F8F4E3', 'Bottle', 'bottle'),
    ('kindle_paperwhite.jpg', '#7D8597', '#F8F4E3', 'Kindle', 'tablet'),
    ('nike_everyday_backpack.jpg', '#2D3142', '#F8F4E3', 'Backpack', 'backpack'),
    ('casio_vintage_watch.jpg', '#BFC0C0', '#1B1B1E', 'Watch', 'watch'),
    ('logitech_mx_master_3s.jpg', '#5C677D', '#F8F4E3', 'Mouse', 'mouse'),
    ('sony_wh_1000xm5.jpg', '#344E41', '#F8F4E3', 'Sony XM5', 'headphones'),
    ('jbl_flip_6.jpg', '#3A86FF', '#F8F4E3', 'Speaker', 'speaker'),
    ('adidas_duffel_bag.jpg', '#3D405B', '#F8F4E3', 'Duffel', 'duffel'),
    ('parker_metal_pen.jpg', '#CED4DA', '#1B1B1E', 'Pen', 'pen'),
    ('samsung_galaxy_buds_2.jpg', '#E9ECEF', '#1B1B1E', 'Buds 2', 'earbuds'),
]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_candidates = [
        'arial.ttf',
        'segoeui.ttf',
        'C:/Windows/Fonts/arial.ttf',
        'C:/Windows/Fonts/segoeui.ttf',
    ]
    for candidate in font_candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_icon(draw: ImageDraw.ImageDraw, kind: str, fg: str) -> None:
    if kind == 'backpack':
        draw.rounded_rectangle((156, 110, 356, 330), radius=36, outline=fg, width=10)
        draw.arc((190, 70, 322, 170), start=200, end=340, fill=fg, width=10)
        draw.line((196, 190, 196, 300), fill=fg, width=8)
        draw.line((316, 190, 316, 300), fill=fg, width=8)
    elif kind == 'headphones':
        draw.arc((130, 90, 382, 290), start=180, end=360, fill=fg, width=14)
        draw.rounded_rectangle((126, 210, 186, 330), radius=18, outline=fg, width=10)
        draw.rounded_rectangle((326, 210, 386, 330), radius=18, outline=fg, width=10)
    elif kind == 'wallet':
        draw.rounded_rectangle((120, 160, 392, 320), radius=28, outline=fg, width=10)
        draw.line((120, 220, 392, 220), fill=fg, width=8)
        draw.ellipse((310, 235, 340, 265), outline=fg, width=6)
    elif kind == 'bottle':
        draw.rounded_rectangle((206, 105, 306, 348), radius=24, outline=fg, width=10)
        draw.rectangle((226, 70, 286, 110), outline=fg, width=10)
    elif kind == 'tablet':
        draw.rounded_rectangle((148, 110, 364, 328), radius=22, outline=fg, width=10)
        draw.ellipse((248, 300, 264, 316), fill=fg)
    elif kind == 'watch':
        draw.rectangle((222, 60, 290, 138), outline=fg, width=10)
        draw.rectangle((222, 330, 290, 438), outline=fg, width=10)
        draw.rounded_rectangle((170, 130, 342, 340), radius=34, outline=fg, width=10)
    elif kind == 'mouse':
        draw.rounded_rectangle((176, 120, 336, 338), radius=80, outline=fg, width=10)
        draw.line((256, 130, 256, 215), fill=fg, width=8)
    elif kind == 'speaker':
        draw.rounded_rectangle((132, 158, 380, 290), radius=28, outline=fg, width=10)
        draw.ellipse((168, 188, 228, 248), outline=fg, width=8)
        draw.ellipse((284, 188, 344, 248), outline=fg, width=8)
    elif kind == 'duffel':
        draw.rounded_rectangle((130, 180, 382, 300), radius=28, outline=fg, width=10)
        draw.arc((190, 120, 322, 220), start=180, end=360, fill=fg, width=10)
        draw.line((170, 210, 130, 255), fill=fg, width=8)
        draw.line((342, 210, 382, 255), fill=fg, width=8)
    elif kind == 'pen':
        draw.line((150, 320, 360, 150), fill=fg, width=14)
        draw.polygon((360, 150, 390, 160, 370, 190), outline=fg, fill=None, width=8)
    elif kind == 'earbuds':
        draw.arc((150, 140, 240, 260), start=180, end=360, fill=fg, width=10)
        draw.line((195, 200, 195, 300), fill=fg, width=8)
        draw.arc((272, 140, 362, 260), start=180, end=360, fill=fg, width=10)
        draw.line((317, 200, 317, 300), fill=fg, width=8)


def main() -> None:
    ensure_directories()
    RAW_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    title_font = load_font(34)
    sub_font = load_font(18)

    for file_name, bg, fg, label, kind in IMAGE_SPECS:
        path = RAW_IMAGES_DIR / file_name
        image = Image.new('RGB', (512, 512), color=bg)
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((24, 24, 488, 488), radius=36, outline=fg, width=6)
        draw.rounded_rectangle((48, 48, 464, 464), radius=28, outline=fg, width=3)
        draw.line((72, 400, 440, 400), fill=fg, width=3)
        draw_icon(draw, kind, fg)
        draw.text((72, 418), label, fill=fg, font=title_font)
        draw.text((72, 458), 'Sample catalog image', fill=fg, font=sub_font)
        image.save(path, quality=95)

    print(f'Created {len(IMAGE_SPECS)} placeholder images in {RAW_IMAGES_DIR}')


if __name__ == '__main__':
    main()
