import pygame
from typing import Tuple, Final

"""Инициализация Pygame"""
pygame.init()

"""Константы экрана"""
SCREEN_WIDTH: Final[int] = 800
SCREEN_HEIGHT: Final[int] = 600
FPS: Final[int] = 60

"""Физические константы"""
GRAVITY: Final[float] = 1.0
JUMP_STRENGTH: Final[float] = 19.8
LOW_JUMP_STRENGTH: Final[float] = 15.0
PLAYER_SPEED: Final[int] = 8
OBSTACLE_SPEED: Final[int] = 7
ITEM_SPEED: Final[int] = 7
BACKGROUND_SPEED: Final[int] = 2
MOUSE_SPEED: Final[int] = 5
BALL_SPEED: Final[int] = 10

"""Цвета"""
WHITE: Final[Tuple[int, int, int]] = (255, 255, 255)
BLACK: Final[Tuple[int, int, int]] = (0, 0, 0)
RED: Final[Tuple[int, int, int]] = (255, 0, 0)
GREEN: Final[Tuple[int, int, int]] = (0, 255, 0)
BLUE: Final[Tuple[int, int, int]] = (0, 0, 255)
YELLOW: Final[Tuple[int, int, int]] = (255, 255, 0)
ORANGE: Final[Tuple[int, int, int]] = (255, 165, 0)
BROWN: Final[Tuple[int, int, int]] = (139, 69, 19)
PURPLE: Final[Tuple[int, int, int]] = (128, 0, 128)
GRAY: Final[Tuple[int, int, int]] = (128, 128, 128)
PINK: Final[Tuple[int, int, int]] = (255, 182, 193)
LIGHT_BLUE: Final[Tuple[int, int, int]] = (173, 216, 230)
LIGHT_GRAY: Final[Tuple[int, int, int]] = (200, 200, 200)
DARK_GRAY: Final[Tuple[int, int, int]] = (100, 100, 100)
GOLD: Final[Tuple[int, int, int]] = (255, 215, 0)

"""Файлы данных"""
HIGH_SCORE_FILE: Final[str] = "high_score.json"
MONEY_SCORE_FILE: Final[str] = "money_score.json"
SHOP_DATA_FILE: Final[str] = "shop.json"

"""Глобальные переменные"""
global_high_score: int = 0
global_money_score: int = 0
score_updated: bool = False
new_record_achieved: bool = False
money_updated: bool = False
selected_accessory_type: int = 0