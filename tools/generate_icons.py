from pathlib import Path
from PIL import Image, ImageDraw

ICONS_DIR = Path(__file__).parent.parent / 'src' / 'assets' / 'icons'
SIZE = 32

SHAPES = {
    'tree': {
        'color': (60, 153, 38),
        'draw': lambda d: (
            d.ellipse([4, 12, 28, 28], fill=(60, 153, 38)),
            d.polygon([(16, 2), (6, 16), (26, 16)], fill=(50, 140, 30)),
        ),
    },
    'stone': {
        'color': (128, 128, 128),
        'draw': lambda d: d.ellipse([4, 10, 28, 28], fill=(128, 128, 128)),
    },
    'cottage': {
        'color': (166, 115, 64),
        'draw': lambda d: (
            d.rectangle([4, 12, 28, 28], fill=(166, 115, 64)),
            d.polygon([(2, 12), (16, 2), (30, 12)], fill=(140, 90, 50)),
        ),
    },
    'statue': {
        'color': (140, 140, 89),
        'draw': lambda d: (
            d.rectangle([10, 6, 22, 16], fill=(140, 140, 89)),   # body
            d.ellipse([10, 0, 22, 10], fill=(150, 150, 95)),     # head
            d.rectangle([8, 16, 12, 22], fill=(130, 130, 80)),   # base left
            d.rectangle([20, 16, 24, 22], fill=(130, 130, 80)),  # base right
        ),
    },
    'flashlight': {
        'color': (230, 217, 51),
        'draw': lambda d: (
            d.rectangle([6, 8, 26, 24], fill=(230, 217, 51)),
            d.ellipse([10, 24, 22, 32], fill=(255, 240, 60)),
        ),
    },
    'target': {
        'color': (204, 64, 51),
        'draw': lambda d: (
            d.ellipse([6, 6, 26, 26], fill=(204, 64, 51)),
            d.ellipse([10, 10, 22, 22], fill=(255, 255, 255)),
            d.ellipse([13, 13, 19, 19], fill=(204, 64, 51)),
        ),
    },
    'fence': {
        'color': (128, 89, 51),
        'draw': lambda d: (
            d.rectangle([2, 10, 30, 14], fill=(128, 89, 51)),
            d.rectangle([2, 20, 30, 24], fill=(128, 89, 51)),
            d.rectangle([4, 4, 8, 28], fill=(128, 89, 51)),
            d.rectangle([14, 4, 18, 28], fill=(128, 89, 51)),
            d.rectangle([24, 4, 28, 28], fill=(128, 89, 51)),
        ),
    },
    'npc': {
        'color': (140, 140, 140),
        'draw': lambda d: (
            d.ellipse([10, 2, 22, 12], fill=(140, 140, 140)),    # head
            d.rectangle([10, 12, 22, 24], fill=(130, 130, 130)), # body
            d.rectangle([4, 18, 10, 24], fill=(120, 120, 120)),  # left arm
            d.rectangle([22, 18, 28, 24], fill=(120, 120, 120)), # right arm
            d.rectangle([10, 24, 16, 30], fill=(120, 120, 120)), # left leg
            d.rectangle([16, 24, 22, 30], fill=(120, 120, 120)), # right leg
        ),
    },
    'player_start': {
        'color': (51, 204, 51),
        'draw': lambda d: (
            d.polygon([(16, 2), (2, 28), (16, 22), (30, 28)], fill=(51, 204, 51)),
        ),
    },
}


def main():
    ICONS_DIR.mkdir(parents=True, exist_ok=True)

    for name, cfg in SHAPES.items():
        img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        cfg['draw'](draw)
        out = ICONS_DIR / f'{name}.png'
        img.save(str(out))
        print(f'  [ok] {name}.png')

    print(f'\nСгенерировано {len(SHAPES)} иконок')


if __name__ == '__main__':
    main()
