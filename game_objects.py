import pygame
import random
from typing import List, Tuple, Optional, Dict, Any
from constants import *


def load_image(name: str, scale: float = 1.0) -> pygame.Surface:
    """Загрузка изображения"""
    image: pygame.Surface = pygame.image.load(name)
    if scale != 1:
        new_size: Tuple[int, int] = (int(image.get_width() * scale), int(image.get_height() * scale))
        image = pygame.transform.scale(image, new_size)
    return image.convert_alpha()


class Ball(pygame.sprite.Sprite):
    """Класс клубка"""
    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self.image: pygame.Surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (200, 200, 255), (14, 14), 14)
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed: int = BALL_SPEED

    def update(self) -> None:
        """Обновляет положение клубка, двигая его вправо"""
        self.rect.x += self.speed
        if self.rect.left > SCREEN_WIDTH:
            self.kill()


class Mouse(pygame.sprite.Sprite):
    """Класс мышей"""
    def __init__(self, target_y: int) -> None:
        super().__init__()
        """Спрайт мыши"""
        self.image: pygame.Surface = pygame.Surface((50, 25), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, GRAY, (0, 5, 35, 15))
        pygame.draw.ellipse(self.image, PINK, (32, 9, 6, 5))
        pygame.draw.circle(self.image, BLACK, (34, 10), 1)
        pygame.draw.circle(self.image, BLACK, (10, 9), 2)
        pygame.draw.circle(self.image, BLACK, (20, 9), 2)
        pygame.draw.circle(self.image, GRAY, (8, 3), 5)
        pygame.draw.circle(self.image, GRAY, (25, 3), 5)
        pygame.draw.circle(self.image, PINK, (8, 3), 2)
        pygame.draw.circle(self.image, PINK, (25, 3), 2)
        pygame.draw.ellipse(self.image, GRAY, (5, 18, 4, 3))
        pygame.draw.ellipse(self.image, GRAY, (15, 18, 4, 3))
        pygame.draw.line(self.image, GRAY, (0, 12), (-12, 12), 2)

        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.left = SCREEN_WIDTH
        self.rect.centery = target_y
        self.speed: int = MOUSE_SPEED

    def update(self) -> None:
        """Обновляет положение мыши, двигая ее влево"""
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()


class Cat(pygame.sprite.Sprite):
    """Класс кота"""
    def __init__(self, cat_stand: List[pygame.Surface], cat_jump: List[pygame.Surface],
                 cat_cloud: List[pygame.Surface], selected_accessory_type: int = 0) -> None:
        super().__init__()
        """Спрайтов для разных состояний"""
        self.cat_stand: List[pygame.Surface] = cat_stand
        self.cat_jump: List[pygame.Surface] = cat_jump
        self.cat_cloud: List[pygame.Surface] = cat_cloud
        self.selected_accessory_type: int = selected_accessory_type

        """Физические параметры кота"""
        self.current_frame: int = 0
        self.velocity_y: float = 0.0
        self.is_jumping: bool = False
        self.is_clouding: bool = False
        self.direction: str = "right"
        self.animation_speed: int = 8
        self.animation_counter: int = 0
        self.can_shoot: bool = True
        self.shoot_cooldown: int = 0
        self.ground_level: int = SCREEN_HEIGHT - 50
        self.mouse_spawn_height: int = SCREEN_HEIGHT - 57
        self.jump_start_y: int = 0
        self.max_jump_height: int = 0
        self.can_pass_high_obstacle: bool = True
        self.update_sprites()
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT - 100)

    def update_sprites(self) -> None:
        """Обновляет спрайты кота в зависимости от выбранного аксессуара"""
        self.stand_frame_right: pygame.Surface = self.cat_stand[self.selected_accessory_type]
        self.jump_frame_right: pygame.Surface = self.cat_jump[self.selected_accessory_type]
        self.cloud_frame_right: pygame.Surface = self.cat_cloud[self.selected_accessory_type]

        """Кадры анимации бега"""
        self.run_frames_right: List[pygame.Surface] = []
        for i in range(2):
            frame: pygame.Surface = self.stand_frame_right.copy()
            if i % 2 == 0:
                frame = pygame.transform.scale(frame, (int(frame.get_width() * 0.9), int(frame.get_height() * 0.95)))
            self.run_frames_right.append(frame)

        """Устанавливаем текущий спрайт в зависимости от состояния"""
        if hasattr(self, 'image'):
            if self.is_jumping:
                self.image = self.jump_frame_right
            elif self.is_clouding:
                self.image = self.cloud_frame_right
            else:
                frame_index: int = self.current_frame % len(self.run_frames_right)
                self.image = self.run_frames_right[frame_index]
        else:
            self.image = self.run_frames_right[0]

    def update(self) -> None:
        """Обновляет состояние кота"""
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
        if self.rect.bottom > self.ground_level:
            self.rect.bottom = self.ground_level
            self.velocity_y = 0.0
            self.is_jumping = False
            self.can_pass_high_obstacle = True

        if self.is_jumping:
            if self.velocity_y > 0 and self.rect.bottom < self.ground_level - 20:
                self.can_pass_high_obstacle = False

            """Макс высота прыжка"""
            current_height: int = self.ground_level - self.rect.bottom
            if current_height > self.max_jump_height:
                self.max_jump_height = current_height

        """Анимация бега"""
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.run_frames_right)

            """Обновляем спрайт в зависимости от состояния"""
            if self.is_jumping:
                self.image = self.jump_frame_right
            elif self.is_clouding:
                self.image = self.cloud_frame_right
            else:
                self.image = self.run_frames_right[self.current_frame]

        if not self.can_shoot:
            self.shoot_cooldown += 1
            if self.shoot_cooldown >= 20:  # Через 20 кадров можно снова стрелять
                self.can_shoot = True
                self.shoot_cooldown = 0

    def jump(self) -> None:
        """Высокий прыжок через препятствия"""
        if not self.is_jumping and not self.is_clouding:
            self.velocity_y = -JUMP_STRENGTH
            self.is_jumping = True
            self.jump_start_y = self.rect.bottom
            self.max_jump_height = 0
            self.can_pass_high_obstacle = True  # В начале прыжка можно перепрыгнуть

    def low_jump(self) -> None:
        """Низкий прыжок через препятствия"""
        if not self.is_jumping and not self.is_clouding:
            self.velocity_y = -LOW_JUMP_STRENGTH
            self.is_jumping = True
            self.jump_start_y = self.rect.bottom
            self.max_jump_height = 0
            self.can_pass_high_obstacle = True

    def cloud(self) -> None:
        """Приседание под облаками"""
        if not self.is_jumping:
            self.is_clouding = True
            old_bottom: int = self.rect.bottom
            old_centerx: int = self.rect.centerx
            self.image = self.cloud_frame_right
            self.rect = self.image.get_rect()
            self.rect.bottom = old_bottom
            self.rect.centerx = old_centerx

    def stand_up(self) -> None:
        """Вставание из приседания"""
        if self.is_clouding:
            self.is_clouding = False
            old_bottom: int = self.rect.bottom
            old_centerx: int = self.rect.centerx
            self.image = self.run_frames_right[self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.bottom = old_bottom
            self.rect.centerx = old_centerx

    def shoot(self) -> Optional[Ball]:
        """Выстрел клубком"""
        if self.can_shoot and not self.is_clouding:  # Нельзя стрелять из приседания
            self.can_shoot = False
            return Ball(self.rect.right, self.rect.centery)
        return None

    def is_standing(self) -> bool:
        """Проверяет, стоит ли кот на земле"""
        return not self.is_jumping and not self.is_clouding and self.rect.bottom == self.ground_level

    def get_mouse_spawn_height(self) -> int:
        """Возвращает высоту, на которой появляются мышки"""
        return self.mouse_spawn_height

    def get_jump_status(self) -> str:
        """Возвращает текущую фазe прыжка"""
        if not self.is_jumping:
            return "На земле"
        elif self.can_pass_high_obstacle:
            return "Начало прыжка"
        else:
            return "Середина/конец прыжка"


class Obstacle(pygame.sprite.Sprite):
    """Класс препятствий"""
    def __init__(self, pregrada_images: List[pygame.Surface], pregrada_types: List[str],
                 is_group: bool = False) -> None:
        super().__init__()
        if is_group:
            valid_indices: List[int] = [i for i, t in enumerate(pregrada_types) if t != "cloud"]
            if not valid_indices:
                index: int = 0
            else:
                index: int = random.choice(valid_indices)
        else:
            index: int = random.randint(0, len(pregrada_images) - 1)

        """Установка изображения"""
        self.image: pygame.Surface = pregrada_images[index]
        self.type: str = pregrada_types[index]
        self.rect: pygame.Rect = self.image.get_rect()

        if self.type == "cloud":
            self.rect.bottom = SCREEN_HEIGHT - 80  # Облака выше
        else:
            self.rect.bottom = SCREEN_HEIGHT - 50  # Обычные препятствия на уровне земли

        self.rect.left = SCREEN_WIDTH  # Появляется справа за экраном

    def update(self) -> None:
        """Движение препятствия влево"""
        self.rect.x -= OBSTACLE_SPEED
        if self.rect.right < 0:
            self.kill()

    @staticmethod
    def can_spawn_group(last_obstacle_rect: Optional[pygame.Rect]) -> bool:
        """Можно ли безопасно создать группу препятствий"""
        if not last_obstacle_rect:
            return True
        distance_to_last: int = SCREEN_WIDTH - last_obstacle_rect.right
        safe_distance: int = 300
        return distance_to_last > safe_distance


class Item(pygame.sprite.Sprite):
    """Класс для собираемых предметов"""
    def __init__(self, type: str) -> None:
        super().__init__()
        self.type: str = type

        """Цвета для разных типов предметов"""
        colors: Dict[str, Tuple[int, int, int]] = {
            "coin": YELLOW,
            "fish": (100, 100, 255),
            "meat": (200, 100, 100),
            "milk": WHITE
        }

        """Размеры для разных типов предметов"""
        sizes: Dict[str, Tuple[int, int]] = {
            "coin": (25, 25),
            "fish": (35, 15),
            "meat": (30, 20),
            "milk": (28, 28)
        }

        """Создание спрайта предмета"""
        self.image: pygame.Surface = pygame.Surface(sizes[type], pygame.SRCALPHA)

        if type == "coin":
            pygame.draw.circle(self.image, YELLOW, (12, 12), 12)
            pygame.draw.circle(self.image, (200, 200, 0), (12, 12), 8)
        elif type == "fish":
            pygame.draw.ellipse(self.image, (100, 100, 255), (0, 0, 30, 15))
            pygame.draw.polygon(self.image, (100, 100, 255), [(30, 7), (35, 2), (35, 12)])
            pygame.draw.circle(self.image, BLACK, (5, 5), 2)
        elif type == "meat":
            pygame.draw.ellipse(self.image, (200, 100, 100), (0, 5, 30, 15))
            pygame.draw.ellipse(self.image, (150, 75, 75), (5, 0, 20, 10))
        elif type == "milk":
            pygame.draw.rect(self.image, WHITE, (5, 5, 18, 18))
            pygame.draw.rect(self.image, (200, 200, 255), (8, 8, 12, 12))
            pygame.draw.rect(self.image, BLUE, (5, 2, 18, 4))

        self.rect: pygame.Rect = self.image.get_rect()

        """Установка начальной позиции"""
        if type == "coin":
            """Монеты появляются на разных высотах"""
            self.rect.y = random.randint(SCREEN_HEIGHT - 200, SCREEN_HEIGHT - 100)
        else:
            self.rect.y = SCREEN_HEIGHT - 70

        self.rect.left = SCREEN_WIDTH

    def update(self) -> None:
        """Движение предмета влево"""
        self.rect.x -= ITEM_SPEED
        """Удаление при выходе за левую границу"""
        if self.rect.right < 0:
            self.kill()