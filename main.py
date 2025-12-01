import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
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

# Создание окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Бегущий кот")
clock = pygame.time.Clock()


# Загрузка изображения name
def load_image(name, scale=1):
    image = pygame.image.load(name)
    if scale != 1:
        new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
        image = pygame.transform.scale(image, new_size)
    return image.convert_alpha()


# Загрузка фонов
backgrounds = []
for i in range(1, 5):
    bg = load_image(f"fon{i}.png")
    if bg.get_width() != SCREEN_WIDTH or bg.get_height() != SCREEN_HEIGHT:
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    backgrounds.append(bg)

current_bg = 0
bg_x = 0

# музыка
music = []
pygame.mixer.init()
pygame.mixer.music.load("music1.mp3")
pygame.mixer.music.play(-1)


# Функция для определения цвета текста в зависимости от фона
def get_text_color():
    if current_bg == 1 or current_bg == 3:
        return WHITE
    else:
        return BLACK


# Загрузка спрайтов кота
cat_stand = load_image("cat1.png", 1.6)
cat_jump = load_image("cat2.png", 1.6)
cat_cloud = load_image("cat3.png", 1.2)

# меняем размеры кота, чтобы создавалась иллюзия движения
cat_run_frames = []
for i in range(2):
    frame = cat_stand.copy()
    if i % 2 == 0:
        frame = pygame.transform.scale(frame, (int(frame.get_width() * 0.9), int(frame.get_height() * 0.95)))
    cat_run_frames.append(frame)


# Класс для кнопок
class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = LIGHT_BLUE
        self.hover_color = (150, 200, 255)
        self.current_color = self.color
        self.font = pygame.font.SysFont('arial', 20)

    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)

        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        if self.rect.collidepoint(pos):
            self.current_color = self.hover_color
            return True
        else:
            self.current_color = self.color
            return False

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            if self.action:
                self.action()
            return True
        return False


# Меню состояния
class GameMenu:
    def __init__(self):
        self.active = False
        self.show_instructions = False
        self.show_shop = False

        # Кнопки главного меню
        center_x = SCREEN_WIDTH // 2
        self.menu_buttons = [
            Button(center_x - 150, 200, 300, 60, "Инструкция", self.show_instructions_menu),
            Button(center_x - 150, 280, 300, 60, "Магазин", self.show_shop_menu),
            Button(center_x - 150, 360, 300, 60, "Продолжить", self.close_menu)
        ]

        # Кнопки магазина
        self.shop_buttons = [
            Button(50, 500, 150, 50, "Купить шляпу (10)", lambda: self.buy_item("hat", 10)),
            Button(250, 500, 150, 50, "Купить очки (20)", lambda: self.buy_item("glasses", 20)),
            Button(450, 500, 150, 50, "Купить бант (15)", lambda: self.buy_item("bow", 15)),
            Button(650, 500, 150, 50, "Назад", self.close_shop)
        ]

        # Кнопка назад для инструкций
        self.back_button = Button(SCREEN_WIDTH // 2 - 75, 500, 150, 50, "Назад", self.close_instructions)

        # Купленные аксессуары
        self.purchased_items = set()
        self.coins = 0

    def show_instructions_menu(self):
        self.show_instructions = True
        self.show_shop = False

    def show_shop_menu(self):
        self.show_shop = True
        self.show_instructions = False

    def close_menu(self):
        self.active = False
        self.show_instructions = False
        self.show_shop = False

    def close_shop(self):
        self.show_shop = False

    def close_instructions(self):
        self.show_instructions = False

    def buy_item(self, item, cost):
        if self.coins >= cost and item not in self.purchased_items:
            self.purchased_items.add(item)
            self.coins -= cost
            print(f"Куплен {item} за {cost} монет")

    def draw(self, surface):
        if not self.active:
            return

        # Полупрозрачный фон
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        if self.show_instructions:
            self.draw_instructions(surface)
        elif self.show_shop:
            self.draw_shop(surface)
        else:
            self.draw_main_menu(surface)

    def draw_main_menu(self, surface):
        # Заголовок
        title_font = pygame.font.SysFont('arial', 48, bold=True)
        title = title_font.render("МЕНЮ ИГРЫ", True, WHITE)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        # Кнопки
        mouse_pos = pygame.mouse.get_pos()
        for button in self.menu_buttons:
            button.check_hover(mouse_pos)
            button.draw(surface)

    def draw_instructions(self, surface):
        # Заголовок
        title_font = pygame.font.SysFont('arial', 40, bold=True)
        title = title_font.render("ИНСТРУКЦИЯ", True, WHITE)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        # Текст инструкции
        font = pygame.font.SysFont('arial', 18)
        instructions = [
            "",
            "",
            "УПРАВЛЕНИЕ:                                                                                                 СОБИРАЙТЕ МОНЕТЫ:",
            "• ПРОБЕЛ - Высокий прыжок через высокие препятствия                          • Монеты (+10 очков)",
            "• СТРЕЛКА ВВЕРХ - Низкий прыжок через низкие препятствия                • Рыба (+15 очков)",
            "• СТРЕЛКА ВНИЗ - Присесть под облаками                                                 • Мясо (+20 очков)",
            "• СТРЕЛКА ВПРАВО - Выстрелить клубком в мышей                                 • Молоко (+25 очков)",
            "• ENTER - Открыть/закрыть меню",
            "• B - Сменить фон",
            "• P - Пауза/продолжить",
            "• R - Перезапуск после проигрыша"
        ]

        y_offset = 100
        for line in instructions:
            text = font.render(line, True, WHITE)
            surface.blit(text, (50, y_offset))
            y_offset += 30

        # Кнопка назад
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.check_hover(mouse_pos)
        self.back_button.draw(surface)

    def draw_shop(self, surface):
        # Заголовок
        title_font = pygame.font.SysFont('arial', 40, bold=True)
        title = title_font.render("МАГАЗИН АКСЕССУАРОВ", True, WHITE)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        # Баланс монет
        font = pygame.font.SysFont('arial', 32)
        balance_text = font.render(f"Монет: {self.coins}", True, WHITE)
        surface.blit(balance_text, (SCREEN_WIDTH // 2 - balance_text.get_width() // 2, 100))

        # Список предметов
        item_font = pygame.font.SysFont('arial', 24)
        items = [
            ("Шляпа", "Модная шляпа для кота", "10 монет", "hat"),
            ("Очки", "Стильные солнцезащитные очки", "20 монет", "glasses"),
            ("Бант", "Элегантный бант на шею", "15 монет", "bow")
        ]

        y_offset = 150
        for name, description, price, item_id in items:
            # Рамка предмета
            pygame.draw.rect(surface, LIGHT_GRAY, (100, y_offset, 600, 80), border_radius=10)
            pygame.draw.rect(surface, DARK_GRAY, (100, y_offset, 600, 80), 2, border_radius=10)

            # Название
            name_text = item_font.render(name, True, BLACK)
            surface.blit(name_text, (120, y_offset + 10))

            # Описание
            desc_font = pygame.font.SysFont('arial', 18)
            desc_text = desc_font.render(description, True, DARK_GRAY)
            surface.blit(desc_text, (120, y_offset + 40))

            # Цена
            price_text = item_font.render(price, True, GRAY if item_id not in self.purchased_items else GREEN)
            surface.blit(price_text, (600, y_offset + 30))

            # Статус
            status_font = pygame.font.SysFont('arial', 18)
            if item_id in self.purchased_items:
                status_text = status_font.render("Куплено", True, GREEN)
                surface.blit(status_text, (620, y_offset + 55))

            y_offset += 100

        # Кнопки
        mouse_pos = pygame.mouse.get_pos()
        for button in self.shop_buttons:
            button.check_hover(mouse_pos)
            button.draw(surface)


# Создаем меню
game_menu = GameMenu()


# выстрел
class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        # Рисуем шар
        pygame.draw.circle(self.image, (200, 200, 255), (14, 14), 14)

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = BALL_SPEED

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > SCREEN_WIDTH:
            self.kill()


# Мышь (враг)
class Mouse(pygame.sprite.Sprite):
    def __init__(self, target_y):
        super().__init__()
        self.image = pygame.Surface((50, 25), pygame.SRCALPHA)
        # Рисуем мышку
        pygame.draw.ellipse(self.image, GRAY, (0, 5, 35, 15))
        pygame.draw.ellipse(self.image, PINK, (32, 9, 6, 5))
        pygame.draw.circle(self.image, BLACK, (34, 10), 1)

        # Глаза
        pygame.draw.circle(self.image, BLACK, (10, 9), 2)
        pygame.draw.circle(self.image, BLACK, (20, 9), 2)

        # Уши
        pygame.draw.circle(self.image, GRAY, (8, 3), 5)
        pygame.draw.circle(self.image, GRAY, (25, 3), 5)
        pygame.draw.circle(self.image, PINK, (8, 3), 2)
        pygame.draw.circle(self.image, PINK, (25, 3), 2)

        # Лапки
        pygame.draw.ellipse(self.image, GRAY, (5, 18, 4, 3))
        pygame.draw.ellipse(self.image, GRAY, (15, 18, 4, 3))

        # Хвост
        pygame.draw.line(self.image, GRAY, (0, 12), (-12, 12), 2)

        self.rect = self.image.get_rect()
        self.rect.left = SCREEN_WIDTH
        self.rect.centery = target_y
        self.speed = MOUSE_SPEED

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()


# Загрузка преград
pregrada_images = []
pregrada_types = []

for i in range(1, 4):
    if i == 2:
        pregrada = load_image(f"pregrada{i}.png", 0.3)
        pregrada_types.append("low_jump")
    elif i == 3:
        pregrada = load_image(f"pregrada{i}.png", 0.50)
        pregrada_types.append("cloud")
    else:
        pregrada = load_image(f"pregrada{i}.png", 0.2)
        pregrada_types.append("jump")

    pregrada_images.append(pregrada)


# Спрайты кота
class Cat(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.run_frames_right = cat_run_frames
        self.jump_frame_right = cat_jump
        self.stand_frame_right = cat_stand
        self.cloud_frame_right = cat_cloud

        self.current_frame = 0
        self.image = self.run_frames_right[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT - 100)
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

    def update(self):
        # Гравитация
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        if self.rect.bottom > self.ground_level:
            self.rect.bottom = self.ground_level
            self.velocity_y = 0
            self.is_jumping = False

        # Плавная смена анимации
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

        # Кулдаун стрельбы
        if not self.can_shoot:
            self.shoot_cooldown += 1
            if self.shoot_cooldown >= 20:
                self.can_shoot = True
                self.shoot_cooldown = 0

    def jump(self):
        if not self.is_jumping and not self.is_clouding:
            self.velocity_y = -JUMP_STRENGTH
            self.is_jumping = True

    def low_jump(self):
        if not self.is_jumping and not self.is_clouding:
            self.velocity_y = -LOW_JUMP_STRENGTH
            self.is_jumping = True

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


# Препятствия
class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
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


# Предметы для сбора
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


# Функция проверки пересечения с препятствиями
def check_collision_with_obstacles(rect):
    for obstacle in obstacles:
        if rect.colliderect(obstacle.rect):
            return True
    return False


# Группы спрайтов
all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
items = pygame.sprite.Group()
mice = pygame.sprite.Group()
yarn_balls = pygame.sprite.Group()

# Создание кота
cat = Cat()
all_sprites.add(cat)

# Переменные игры
score = 0
coins = 0
food = 0
milk = 0
mice_killed = 0
high_score = 0
game_over = False
game_paused = False
spawn_timer = 0
item_timer = 0
mouse_timer = 0
next_mouse_spawn = random.randint(180, 360)
font = pygame.font.SysFont('arial', 20)
small_font = pygame.font.SysFont('arial', 16)
title_font = pygame.font.SysFont('arial', 36, bold=True)


# Функция отрисовки текста
def draw_text(text, color, x, y, font_obj=font):
    img = font_obj.render(text, True, color)
    screen.blit(img, (x, y))


# Функция сброса игры
def reset_game():
    global score, coins, food, milk, mice_killed, game_over, game_paused, spawn_timer, item_timer, mouse_timer, next_mouse_spawn
    for sprite in all_sprites:
        if sprite != cat:
            sprite.kill()

    score = 0
    coins = 0
    food = 0
    milk = 0
    mice_killed = 0
    game_over = False
    game_paused = False
    spawn_timer = 0
    item_timer = 0
    mouse_timer = 0
    next_mouse_spawn = random.randint(180, 360)

    cat.rect.center = (100, SCREEN_HEIGHT - 100)
    cat.velocity_y = 0
    cat.is_jumping = False
    cat.is_clouding = False
    cat.can_shoot = True
    cat.shoot_cooldown = 0


# Функция для определения позиции текста статистики
def get_stats_position():
    base_x = SCREEN_WIDTH - 150
    test_text = f"Счет: {int(score)}"
    test_surface = font.render(test_text, True, WHITE)
    return base_x


# Главный игровой цикл
running = True
while running:
    clock.tick(FPS)

    # Обновляем количество монет в меню
    game_menu.coins = coins

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # Enter
                if not game_over:
                    game_menu.active = not game_menu.active

            if not game_menu.active:  # Только если меню не активно
                if event.key == pygame.K_p or event.key == ord('з'):
                    game_paused = not game_paused
                elif not game_paused and not game_over:
                    if event.key == pygame.K_SPACE:
                        cat.jump()
                    elif event.key == pygame.K_UP:
                        cat.low_jump()
                    elif event.key == pygame.K_DOWN:
                        cat.cloud()
                    elif event.key == pygame.K_RIGHT:
                        yarn_ball = cat.shoot()
                        if yarn_ball:
                            yarn_balls.add(yarn_ball)
                            all_sprites.add(yarn_ball)
                    elif event.key == pygame.K_b or event.key == ord('и'):
                        current_bg = (current_bg + 1) % len(backgrounds)
                elif (event.key == pygame.K_r or event.key == ord('к')) and game_over:
                    reset_game()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and game_menu.active:  # Левая кнопка мыши
                mouse_pos = pygame.mouse.get_pos()
                if game_menu.show_instructions:
                    game_menu.back_button.check_click(mouse_pos)
                elif game_menu.show_shop:
                    for button in game_menu.shop_buttons:
                        button.check_click(mouse_pos)
                else:
                    for button in game_menu.menu_buttons:
                        button.check_click(mouse_pos)

    # Проверяем наведение мыши на кнопки
    if game_menu.active:
        mouse_pos = pygame.mouse.get_pos()
        if game_menu.show_instructions:
            game_menu.back_button.check_hover(mouse_pos)
        elif game_menu.show_shop:
            for button in game_menu.shop_buttons:
                button.check_hover(mouse_pos)
        else:
            for button in game_menu.menu_buttons:
                button.check_hover(mouse_pos)

    keys = pygame.key.get_pressed()
    if not keys[pygame.K_DOWN]:
        cat.stand_up()

    if not game_over and not game_paused and not game_menu.active:
        all_sprites.update()

        bg_x -= BACKGROUND_SPEED
        if bg_x <= -SCREEN_WIDTH:
            bg_x = 0

        # Спавн препятствий
        spawn_timer += 1
        if spawn_timer >= 90:
            spawn_timer = 0
            obstacle = Obstacle()
            obstacles.add(obstacle)
            all_sprites.add(obstacle)

        # Спавн предметов
        item_timer += 1
        if item_timer >= 45:
            item_timer = 0
            item_type = random.choice(["coin", "fish", "meat", "milk"])

            max_attempts = 10
            for attempt in range(max_attempts):
                item = Item(item_type)

                if not check_collision_with_obstacles(item.rect):
                    items.add(item)
                    all_sprites.add(item)
                    break
                else:
                    item.kill()

        # Спавн мышек
        mouse_timer += 1
        if mouse_timer >= next_mouse_spawn:
            mouse_timer = 0
            next_mouse_spawn = random.randint(180, 480)

            mouse = Mouse(cat.get_mouse_spawn_height())
            mice.add(mouse)
            all_sprites.add(mouse)

        # Проверка столкновений с препятствиями
        hits = pygame.sprite.spritecollide(cat, obstacles, False)
        for hit in hits:
            if hit.type == "jump" and not cat.is_jumping:
                game_over = True
            elif hit.type == "low_jump" and not cat.is_jumping:
                game_over = True
            elif hit.type == "cloud" and not cat.is_clouding:
                game_over = True

        # Проверка столкновений с мышками
        mouse_hits = pygame.sprite.spritecollide(cat, mice, False)
        if mouse_hits:
            game_over = True

        # Проверка попадания клубков в мышек
        for yarn_ball in yarn_balls:
            mouse_hits = pygame.sprite.spritecollide(yarn_ball, mice, True)
            for mouse in mouse_hits:
                yarn_ball.kill()
                mice_killed += 1
                score += 50

        # Проверка сбора предметов
        collected = pygame.sprite.spritecollide(cat, items, True)
        for item in collected:
            if item.type == "coin":
                coins += 1
                score += 10
            elif item.type == "fish":
                food += 1
                score += 15
            elif item.type == "meat":
                food += 2
                score += 20
            elif item.type == "milk":
                milk += 1
                score += 25

        score += 0.2

        if score > high_score:
            high_score = score

    # Рисуем фоны
    screen.blit(backgrounds[current_bg], (bg_x, 0))
    screen.blit(backgrounds[current_bg], (bg_x + SCREEN_WIDTH, 0))

    # Нижняя дощечка
    pygame.draw.rect(screen, BROWN, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
    for i in range(0, SCREEN_WIDTH, 20):
        pygame.draw.line(screen, (110, 60, 30), (i, SCREEN_HEIGHT - 50), (i, SCREEN_HEIGHT), 1)

    all_sprites.draw(screen)

    text_color = get_text_color()
    stats_x = get_stats_position()

    # Отрисовка статистики
    draw_text(f"Рекорд: {int(high_score)}", text_color, stats_x, 10)
    draw_text(f"Монеты: {coins}", text_color, stats_x, 35)
    draw_text(f"Еда: {food}", text_color, stats_x, 60)
    draw_text(f"Молоко: {milk}", text_color, stats_x, 85)
    draw_text(f"Мыши: {mice_killed}", text_color, stats_x, 110)
    draw_text(f"Счет: {int(score)}", text_color, stats_x, 135)

    # Подсказка про меню
    if not game_menu.active and not game_over:
        draw_text("Нажмите ENTER для открытия меню", text_color, 10, SCREEN_HEIGHT - 30, small_font)

    # Экран паузы
    if game_paused and not game_over and not game_menu.active:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        draw_text("ПАУЗА", WHITE, SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 40, title_font)
        draw_text("Нажми P для продолжения", WHITE, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 10, small_font)

    # Экран Game Over
    if game_over and not game_menu.active:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        draw_text("GAME OVER", RED, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 80, title_font)
        draw_text(f"Финальный счет: {int(score)}", WHITE, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 20)
        draw_text(f"Собрано монет: {coins}", WHITE, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 10)
        draw_text(f"Собрано еды: {food}", WHITE, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 40)
        draw_text(f"Собрано молока: {milk}", WHITE, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 70)
        draw_text(f"Убито мышек: {mice_killed}", WHITE, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 100)
        draw_text("Нажми R для перезапуска", WHITE, SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 + 140, small_font)

    # Отрисовка меню
    game_menu.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()