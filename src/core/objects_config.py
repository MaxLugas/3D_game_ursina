# ================ Коллайдеры | Colliders ================
COLLIDER_SHRINK_FACTOR = 0.8                            # Базовый коэффициент уменьшения коллайдера | Base collider shrink factor
STONE_COLLIDER_SHRINK = 0.5                              # Уменьшение коллайдера для камней (по X/Z) | Collider shrink for STONEs (X/Z axes)
TREE_COLLIDER_SHRINK = 0.5                              # Уменьшение коллайдера для деревьев | Collider shrink for trees
COTTAGE_COLLIDER_SHRINK = 0.2                           # Уменьшение коллайдера для домиков | Collider shrink for cottages
FLASHLIGHT_COLLIDER_SHRINK = 0.2                        # Уменьшение коллайдера для фонариков | Collider shrink for flashlights
TARGET_COLLIDER_SHRINK = 1                              # Уменьшение коллайдера для мишеней | Collider shrink for targets
STATUE_COLLIDER_SHRINK = 1                              # Коллайдер статуи = размер модели | Statue collider matches model size
FENCE_COLLIDER_SHRINK=1


# ================ Размер | Scale ================
STONE_SCALE=1.5
TARGET_SCALE=1
TREE_SCALE=2
COTTAGE_SCALE=5
FLASHLIGHT_SCALE=3
STATUE_SCALE=0.5
FENCE_SCALE=1
PLAYER_SPAWN_SCALE=2

# ================ Конфигурация объектов мира | World objects configuration ================
OBJECT_CONFIGS = {
    "stone": {
        "model": "stone",
        "scale": STONE_SCALE,
        "shrink_factor": STONE_COLLIDER_SHRINK,
        "y_offset": 0,
        "enabled": False
    },
    "target": {
        "model": "target",
        "scale": TARGET_SCALE,
        "shrink_factor": TARGET_COLLIDER_SHRINK,
        "y_offset": 0,
        "enabled": False
    },
    "tree": {
        "model": "tree",
        "scale": TREE_SCALE,
        "shrink_factor": TREE_COLLIDER_SHRINK,
        "y_offset": 0,
        "has_specular": True,
        "enabled": False
    },
    "cottage": {
        "model": "cottage",
        "scale": COTTAGE_SCALE,
        "shrink_factor": COTTAGE_COLLIDER_SHRINK,
        "y_offset": 0,
        "enabled": False
    },
    "flashlight": {
        "model": "flashlight",
        "scale": FLASHLIGHT_SCALE,
        "shrink_factor": FLASHLIGHT_COLLIDER_SHRINK,
        "collider": "box",
        "y_offset": 0,
        "enabled": False
    },
    "statue": {
        "model": "statue",
        "scale": STATUE_SCALE,
        "shrink_factor": None,
        "collider": "box",
        "y_offset": 0,
        "is_statue": True,
        "enabled": True
    },
    "fence": {
        "model": "fence",
        "scale": FENCE_SCALE,
        "shrink_factor": FENCE_COLLIDER_SHRINK,
        "collider": "box",
        "y_offset": 0,
        "enabled": True
    }
}
