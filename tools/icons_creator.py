import pygame
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import ICONS_DIR


def create_icon_files():
    pygame.init()

    ICONS_DIR.mkdir(parents=True, exist_ok=True)

    # Размер иконки | Icon size
    size = 32

    # Цвета | Colors
    colors = {
        'tree': (34, 170, 34),
        'rock': (170, 85, 34),
        'cottage': (170, 68, 170),
        'statue': (170, 170, 255),
        'flashlight': (255, 255, 170),
        'target': (255, 85, 85),
        'npc': (255, 0, 0),
        'player_start': (0, 100, 255)
    }

    # Иконку дерева | Tree icon
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    # Крона | Crown
    pygame.draw.circle(surf, colors['tree'], (16, 12), 8)
    # Ствол | Trunk
    pygame.draw.rect(surf, (139, 69, 19), (14, 18, 4, 12))
    pygame.image.save(surf, ICONS_DIR / "tree.png")

    # Иконка камня | Rock icon
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surf, colors['rock'], (10, 18), 6)
    pygame.draw.circle(surf, colors['rock'], (22, 18), 6)
    pygame.draw.circle(surf, colors['rock'], (16, 12), 6)
    pygame.image.save(surf, ICONS_DIR / "rock.png")

    # Иконка домика | Cottage icon
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    # Крыша | Roof
    pygame.draw.polygon(surf, colors['cottage'], [(16, 4), (28, 12), (4, 12)])
    # Основание | Base
    pygame.draw.rect(surf, colors['cottage'], (8, 12, 16, 16))
    pygame.image.save(surf, ICONS_DIR / "cottage.png")

    # Иконка статуи | Statue icon
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    # Голова | Head
    pygame.draw.circle(surf, colors['statue'], (16, 10), 6)
    # Тело | Body
    pygame.draw.rect(surf, colors['statue'], (12, 16, 8, 14))
    pygame.image.save(surf, ICONS_DIR / "statue.png")

    # Иконка фонарика | Flashlight icon
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    # Корпус | Body
    pygame.draw.rect(surf, colors['flashlight'], (12, 10, 8, 16))
    # Лампочка | Flashlight
    pygame.draw.circle(surf, colors['flashlight'], (16, 10), 6)
    pygame.image.save(surf, ICONS_DIR / "flashlight.png")

    # Иконка мишени | Target icon
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surf, colors['target'], (16, 16), 12, 2)
    pygame.draw.circle(surf, colors['target'], (16, 16), 6, 2)
    pygame.draw.circle(surf, colors['target'], (16, 16), 2)
    pygame.image.save(surf, ICONS_DIR / "target.png")

    # Иконка NPC | NPC icon
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    # Голова | Head
    pygame.draw.circle(surf, colors['npc'], (16, 10), 6)
    # Тело | Body
    pygame.draw.line(surf, colors['npc'], (16, 16), (16, 26), 3)
    # Руки | Hands
    pygame.draw.line(surf, colors['npc'], (16, 20), (8, 24), 3)
    pygame.draw.line(surf, colors['npc'], (16, 20), (24, 24), 3)
    pygame.image.save(surf, ICONS_DIR / "npc.png")

    # Иконка игрока | Player icon
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    icon_color = colors['player_start']
    center_x = size // 2
    # Рисуем голову | Draw head
    head_radius = 8
    head_y = 10
    pygame.draw.circle(surf, icon_color, (center_x, head_y), head_radius)

    # Рисуем тело | Draw body
    shoulders = [
        (center_x - 8, head_y + 8),
        (center_x + 8, head_y + 8),
        (center_x + 13, size - 6),
        (center_x - 13, size - 6)
    ]
    pygame.draw.polygon(surf, icon_color, shoulders)
    pygame.image.save(surf, ICONS_DIR / "player_start.png")

    print(f"Иконки созданы: {ICONS_DIR} | Icons created: {ICONS_DIR}")
    print("Созданные файлы | Created files:")
    for file in sorted(ICONS_DIR.glob("*.png")):
        print(f"  - {file.name}")

if __name__ == "__main__":
    create_icon_files()