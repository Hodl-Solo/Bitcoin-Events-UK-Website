#!/usr/bin/env python3
"""Build web-friendly meetup logo thumbnails from the artwork archive."""

from pathlib import Path
from PIL import Image, ImageOps

SOURCE_DIR = Path('assets/meetup-artwork/All meetup artwork')
OUTPUT_DIR = Path('assets/meetup-logos')

LOGOS = {
    'battersea-bitcoiners': 'Battersea Bitcoiners.JPG',
    'berkshire-bitcoiners': 'Berkshire Bitcoin Logo sq.png',
    'bitcoin-beach-bournemouth': 'Bournemouth Logo.png',
    'chilterns-bitcoin-hub': 'Chilterns logo.png',
    'city-financial-bitcoiners': 'city and financial.jpg',
    'cyphermunk-house': 'cyphermunk house.JPG',
    'leamington-spa-bitcoin': 'Leam Bitcoin.png',
    'northamptonshire-bitcoin-network': 'Northants Bitcoin logo round.png',
    'bitcoin-surrey': 'Surrey logo.png',
    'sutton-coldfield-bitcoin': 'Sutton Logo.PNG',
    'sheffield-bitcoin': 'Bitcoin Sheffield logo.png',
    'bitcoin-wales': 'BitcoinWalesLogo.png',
    'bitcoin-power-ayrshire': 'Ayr Scotland.png',
    'bitcoin-derby': 'Derby logo.JPG',
    'dundee-bitcoin': 'Dundee Logo.png',
    'glasgow-bitcoin': 'glasgow logo.png',
    'kent-bitcoin': 'kent.PNG',
    'lake-district-btc': 'lake district.JPG',
    'limerick-bitcoin': 'limerick.png',
    'liverpool-bitcoin': 'liverpool.JPG',
    'newcastle-bitcoin-coffee': 'newcastle.JPG',
    'preston-bitcoin': 'preston.JPG',
    'real-bedford-fc': 'real bedford.PNG',
    'women-of-bitcoin-uk': 'women of bitcoin 300.png',
}

SIZE = (320, 320)
INNER = (292, 292)


def build_logo(slug: str, filename: str):
    src = SOURCE_DIR / filename
    if not src.exists():
        print(f'SKIP missing: {src}')
        return

    with Image.open(src) as image:
        image = image.convert('RGBA')
        fitted = ImageOps.contain(image, INNER, Image.Resampling.LANCZOS)
        canvas = Image.new('RGBA', SIZE, (0, 0, 0, 0))
        x = (SIZE[0] - fitted.width) // 2
        y = (SIZE[1] - fitted.height) // 2
        canvas.alpha_composite(fitted, (x, y))
        out = OUTPUT_DIR / f'{slug}.webp'
        canvas.save(out, 'WEBP', quality=84, method=6)
        print(f'{filename} -> {out}')


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUTPUT_DIR.glob('*.webp'):
        old.unlink()
    for slug, filename in LOGOS.items():
        build_logo(slug, filename)


if __name__ == '__main__':
    main()
