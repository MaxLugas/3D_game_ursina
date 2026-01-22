from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import *

class DoubleJumpPlayer(FirstPersonController):
    # Настройки по умолчанию — менять ТОЛЬКО здесь!
    DEFAULT_JUMP_HEIGHT = 2.0          # первый прыжок
    DEFAULT_SECOND_JUMP_HEIGHT = 3.0   # второй прыжок

    def __init__(self, **kwargs):
        # Извлекаем параметры, специфичные для двойного прыжка
        jump_height = kwargs.pop('jump_height', self.DEFAULT_JUMP_HEIGHT)
        self.second_jump_height = kwargs.pop('second_jump_height', self.DEFAULT_SECOND_JUMP_HEIGHT)

        # Передаём оставшиеся параметры родителю
        super().__init__(jump_height=jump_height, **kwargs)

        # Флаг: использован ли второй прыжок
        self.double_jump_used = False

    def input(self, key):
        if key == 'space':
            if self.grounded:
                # Первый прыжок — стандартный
                super().input('space')
                self.double_jump_used = False
            elif not self.double_jump_used:
                # Второй прыжок — временно подменяем состояние
                original_grounded = self.grounded
                original_jump = self.jump_height

                self.grounded = True
                self.jump_height = self.second_jump_height
                super().input('space')

                # Восстанавливаем оригинальные значения
                self.jump_height = original_jump
                self.grounded = original_grounded

                self.double_jump_used = True
        return False