import pygame
import random
from constants import *


def load_image(name, scale=1):
    image = pygame.image.load(name)
    if scale != 1:
        new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
        image = pygame.transform.scale(image, new_size)
    return image.convert_alpha()


class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (200, 200, 255), (14, 14), 14)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = BALL_SPEED

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > SCREEN_WIDTH:
            self.kill()


class Mouse(pygame.sprite.Sprite):
    def __init__(self, target_y):
        super().__init__()
        self.image = pygame.Surface((50, 25), pygame.SRCALPHA)
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

        self.rect = self.image.get_rect()
        self.rect.left = SCREEN_WIDTH
        self.rect.centery = target_y
        self.speed = MOUSE_SPEED

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()


class Cat(pygame.sprite.Sprite):
    def __init__(self, cat_stand, cat_jump, cat_cloud, selected_accessory_type=0):
        super().__init__()
        self.cat_stand = cat_stand
        self.cat_jump = cat_jump
        self.cat_cloud = cat_cloud
        self.selected_accessory_type = selected_accessory_type

        self.current_frame = 0
        self.velocity_y = 0
        self.is_jumping = False
        self.is_clouding = False
        self.direction = "right"
        self.animation_speed = 8
        self.animation_counter = 0
        self.can_shoot = True
        self.shoot_cooldown = 0
        self.ground_level = SCREEN_HEIGHT - 50
        self.mouse_spawn_height = SCREEN_HEIGHT - 57
        self.jump_start_y = 0
        self.max_jump_height = 0
        self.can_pass_high_obstacle = True

        self.update_sprites()
        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT - 100)

    def update_sprites(self):
        self.stand_frame_right = self.cat_stand[self.selected_accessory_type]
        self.jump_frame_right = self.cat_jump[self.selected_accessory_type]
        self.cloud_frame_right = self.cat_cloud[self.selected_accessory_type]

        self.run_frames_right = []
        for i in range(2):
            frame = self.stand_frame_right.copy()
            if i % 2 == 0:
                frame = pygame.transform.scale(frame, (int(frame.get_width() * 0.9), int(frame.get_height() * 0.95)))
            self.run_frames_right.append(frame)

        if hasattr(self, 'image'):
            if self.is_jumping:
                self.image = self.jump_frame_right
            elif self.is_clouding:
                self.image = self.cloud_frame_right
            else:
                frame_index = self.current_frame % len(self.run_frames_right)
                self.image = self.run_frames_right[frame_index]
        else:
            self.image = self.run_frames_right[0]

    def update(self):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        if self.rect.bottom > self.ground_level:
            self.rect.bottom = self.ground_level
            self.velocity_y = 0
            self.is_jumping = False
            self.can_pass_high_obstacle = True

        if self.is_jumping:
            if self.velocity_y > 0 and self.rect.bottom < self.ground_level - 20:
                self.can_pass_high_obstacle = False

            current_height = self.ground_level - self.rect.bottom
            if current_height > self.max_jump_height:
                self.max_jump_height = current_height

        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.run_frames_right)

            if self.is_jumping:
                self.image = self.jump_frame_right
            elif self.is_clouding:
                self.image = self.cloud_frame_right
            else:
                self.image = self.run_frames_right[self.current_frame]

        if not self.can_shoot:
            self.shoot_cooldown += 1
            if self.shoot_cooldown >= 20:
                self.can_shoot = True
                self.shoot_cooldown = 0

    def jump(self):
        if not self.is_jumping and not self.is_clouding:
            self.velocity_y = -JUMP_STRENGTH
            self.is_jumping = True
            self.jump_start_y = self.rect.bottom
            self.max_jump_height = 0
            self.can_pass_high_obstacle = True

    def low_jump(self):
        if not self.is_jumping and not self.is_clouding:
            self.velocity_y = -LOW_JUMP_STRENGTH
            self.is_jumping = True
            self.jump_start_y = self.rect.bottom
            self.max_jump_height = 0
            self.can_pass_high_obstacle = True

    def cloud(self):
        if not self.is_jumping:
            self.is_clouding = True
            old_bottom = self.rect.bottom
            old_centerx = self.rect.centerx
            self.image = self.cloud_frame_right
            self.rect = self.image.get_rect()
            self.rect.bottom = old_bottom
            self.rect.centerx = old_centerx

    def stand_up(self):
        if self.is_clouding:
            self.is_clouding = False
            old_bottom = self.rect.bottom
            old_centerx = self.rect.centerx
            self.image = self.run_frames_right[self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.bottom = old_bottom
            self.rect.centerx = old_centerx

    def shoot(self):
        if self.can_shoot and not self.is_clouding:
            self.can_shoot = False
            return Ball(self.rect.right, self.rect.centery)
        return None

    def is_standing(self):
        return not self.is_jumping and not self.is_clouding and self.rect.bottom == self.ground_level

    def get_mouse_spawn_height(self):
        return self.mouse_spawn_height

    def get_jump_status(self):
        if not self.is_jumping:
            return "На земле"
        elif self.can_pass_high_obstacle:
            return "Начало прыжка"
        else:
            return "Середина/конец прыжка"


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, pregrada_images, pregrada_types, is_group=False):
        super().__init__()

        # Если это часть группы, исключаем облака из возможных типов
        if is_group:
            # Создаем списки индексов, которые НЕ являются облаками
            valid_indices = [i for i, t in enumerate(pregrada_types) if t != "cloud"]
            if not valid_indices:
                # Если вдруг нет подходящих препятствий (только облака), используем первый
                index = 0
            else:
                index = random.choice(valid_indices)
        else:
            # Обычный выбор (все типы доступны)
            index = random.randint(0, len(pregrada_images) - 1)

        self.image = pregrada_images[index]
        self.type = pregrada_types[index]
        self.rect = self.image.get_rect()

        if self.type == "cloud":
            self.rect.bottom = SCREEN_HEIGHT - 80
        else:
            self.rect.bottom = SCREEN_HEIGHT - 50

        self.rect.left = SCREEN_WIDTH

    def update(self):
        self.rect.x -= OBSTACLE_SPEED
        if self.rect.right < 0:
            self.kill()

    @staticmethod
    def can_spawn_group(last_obstacle_rect):
        """Проверяет, можно ли безопасно заспавнить группу"""
        if not last_obstacle_rect:
            return True

        # Проверяем расстояние до последнего препятствия
        distance_to_last = SCREEN_WIDTH - last_obstacle_rect.right
        safe_distance = 300  # Минимальное расстояние для группового спавна

        return distance_to_last > safe_distance


class Item(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        self.type = type

        colors = {
            "coin": YELLOW,
            "fish": (100, 100, 255),
            "meat": (200, 100, 100),
            "milk": WHITE
        }

        sizes = {
            "coin": (25, 25),
            "fish": (35, 15),
            "meat": (30, 20),
            "milk": (28, 28)
        }

        self.image = pygame.Surface(sizes[type], pygame.SRCALPHA)

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

        self.rect = self.image.get_rect()

        if type == "coin":
            self.rect.y = random.randint(SCREEN_HEIGHT - 200, SCREEN_HEIGHT - 100)
        else:
            self.rect.y = SCREEN_HEIGHT - 70

        self.rect.left = SCREEN_WIDTH

    def update(self):
        self.rect.x -= ITEM_SPEED
        if self.rect.right < 0:
            self.kill()