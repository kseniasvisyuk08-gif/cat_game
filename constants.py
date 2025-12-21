import pygame

# Инициализация Pygame
pygame.init()

# Константы экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Физические константы
GRAVITY = 1
JUMP_STRENGTH = 19.8
LOW_JUMP_STRENGTH = 15
PLAYER_SPEED = 8
OBSTACLE_SPEED = 7
ITEM_SPEED = 7
BACKGROUND_SPEED = 2
MOUSE_SPEED = 5
BALL_SPEED = 10

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
PINK = (255, 182, 193)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
GOLD = (255, 215, 0)

# Файлы данных
HIGH_SCORE_FILE = "high_score.json"
MONEY_SCORE_FILE = "money_score.json"
SHOP_DATA_FILE = "shop.json"

# Глобальные переменные
global_high_score = 0
global_money_score = 0
score_updated = False
new_record_achieved = False
money_updated = False
selected_accessory_type = 0