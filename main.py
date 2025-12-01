import pygame
import random
import sys

# Инициализация Pygame
pygame.init() #инициализируем библиотеку, чтобы использовать функции

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

#Создание окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) #задаем размеры экрана
pygame.display.set_caption("Бегущий кот") #задает название игры(сверху)
clock = pygame.time.Clock()


#Загрузка изображения name
def load_image(name, scale=1):
    image = pygame.image.load(name) #загрузка изображения по заданному пути
    if scale != 1:
        new_size = (int(image.get_width() * scale), int(image.get_height() * scale)) #get_width/get_height-функции из pygame
        image = pygame.transform.scale(image, new_size) #меняет масштаб изображения на заданный в предыдущей строке
    return image.convert_alpha() #заменяем прозрачные пиксели на черный



#Загрузка фонов
backgrounds = []
for i in range(1, 5): #цикл для загрузки 4 фонов
    bg = load_image(f"fon{i}.png") #загружен файлы, которые отвечают за фон
    if bg.get_width() != SCREEN_WIDTH or bg.get_height() != SCREEN_HEIGHT: #меняем размер фона на размер экрана
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    backgrounds.append(bg)

current_bg = 0
bg_x = 0

#music
# музыка
music = []
pygame.mixer.init()
pygame.mixer.music.load("music1.mp3")
pygame.mixer.music.play(-1)


#Функция для определения цвета текста в зависимости от фона
def get_text_color():
    if current_bg == 1 or current_bg == 3:
        return WHITE
    else:
        return BLACK


#Загрузка спрайтов кота
cat_stand = load_image("cat1.png", 1.6)
cat_jump = load_image("cat2.png", 1.6)
cat_cloud = load_image("cat3.png", 1.2)

#меняем размеры кота, чтобы создавалась иллюзия движения
cat_run_frames = []
for i in range(2):
    frame = cat_stand.copy()
    if i % 2 == 0:
        frame = pygame.transform.scale(frame, (int(frame.get_width() * 0.9), int(frame.get_height() * 0.95)))
    cat_run_frames.append(frame)


#выстрел
class Ball(pygame.sprite.Sprite): #pygame.sprite.Sprite-класс в pygame, который работает с спрайтами для 2d-графики
    def __init__(self, x, y):
        super().__init__() #метод, соединяющий pygame.sprite.Sprite
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA) #создаем поле под шар
        # Рисуем шар
        pygame.draw.circle(self.image, (200, 200, 255), (14, 14), 14)

        self.rect = self.image.get_rect() #создаем прямоугольное пространство, под мяч
        self.rect.centerx = x #задаем центр мяча
        self.rect.centery = y
        self.speed = BALL_SPEED #задаем скорость движения шара

    #перемещение шара
    def update(self):
        self.rect.x += self.speed
        if self.rect.left > SCREEN_WIDTH: #проверка на выход шара за правую границу
            self.kill()


#Мышь (враг)
class Mouse(pygame.sprite.Sprite):
    def __init__(self, target_y):
        super().__init__()
        self.image = pygame.Surface((50, 25), pygame.SRCALPHA)  # Увеличили ширину для хвоста
        # Рисуем мышку
        pygame.draw.ellipse(self.image, GRAY, (0, 5, 35, 15))  # Тело
        pygame.draw.ellipse(self.image, PINK, (32, 9, 6, 5))  # Носик
        pygame.draw.circle(self.image, BLACK, (34, 10), 1)  # Ноздря

        # Глаза
        pygame.draw.circle(self.image, BLACK, (10, 9), 2)  # Левый глаз
        pygame.draw.circle(self.image, BLACK, (20, 9), 2)  # Правый глаз

        # Уши
        pygame.draw.circle(self.image, GRAY, (8, 3), 5)  # Левое ухо
        pygame.draw.circle(self.image, GRAY, (25, 3), 5)  # Правое ухо
        pygame.draw.circle(self.image, PINK, (8, 3), 2)  # Внутреннее левое ухо
        pygame.draw.circle(self.image, PINK, (25, 3), 2)  # Внутреннее правое ухо

        # Лапки
        pygame.draw.ellipse(self.image, GRAY, (5, 18, 4, 3))  # Передняя лапка
        pygame.draw.ellipse(self.image, GRAY, (15, 18, 4, 3))  # Задняя лапка

        # Хвост
        pygame.draw.line(self.image, GRAY, (0, 12), (-12, 12), 2)

        self.rect = self.image.get_rect()
        # Появляется с правого края на фиксированной высоте (ниже)
        self.rect.left = SCREEN_WIDTH
        self.rect.centery = target_y  # Фиксированная высота
        self.speed = MOUSE_SPEED

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()


#Загрузка преград
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

#Спрайты кота
class Cat(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        #задаем спрайты  на все состояния кота
        self.run_frames_right = cat_run_frames
        self.jump_frame_right = cat_jump
        self.stand_frame_right = cat_stand
        self.cloud_frame_right = cat_cloud

        self.current_frame = 0
        self.image = self.run_frames_right[self.current_frame] #отображение текущнго спрайта через массив спрайтов
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
        # Запоминаем уровень земли кота
        self.ground_level = SCREEN_HEIGHT - 50
        # Фиксированная высота для мышей - НИЖЕ центра кота
        self.mouse_spawn_height = SCREEN_HEIGHT - 57  # Мыши появляются ближе к земле

    def update(self):
        # Гравитация
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        #проверка находится ли кот на земле
        if self.rect.bottom > self.ground_level:
            self.rect.bottom = self.ground_level
            self.velocity_y = 0
            self.is_jumping = False

        #Плавная смена анимации
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.run_frames_right)

            #смена картинок при различных действиях
            if self.is_jumping:
                self.image = self.jump_frame_right
            elif self.is_clouding:
                self.image = self.cloud_frame_right
            else:
                self.image = self.run_frames_right[self.current_frame]

        #кулдаун стрельбы, чтобы между выстрелами были промежутки
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
        # Проверяет, стоит ли кот нормально (не прыгает и не приседает)
        return not self.is_jumping and not self.is_clouding and self.rect.bottom == self.ground_level

    def get_mouse_spawn_height(self):
        # Возвращает фиксированную высоту для появления мышей (НИЖЕ)
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

        self.rect.left = SCREEN_WIDTH #чтобы препятствия появлялись только справа

    def update(self): #удаление препятствий при их касании левого края окна
        self.rect.x -= OBSTACLE_SPEED
        if self.rect.right < 0:
            self.kill()


#Предметы для сбора
class Item(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        self.type = type #присваиваем тип объекта

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

        self.image = pygame.Surface(sizes[type], pygame.SRCALPHA) #прозрачная поверхность

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

        self.rect = self.image.get_rect() #создает прямоугольник под изображение

        if type == "coin":
            self.rect.y = random.randint(SCREEN_HEIGHT - 200, SCREEN_HEIGHT - 100)
        else:
            self.rect.y = SCREEN_HEIGHT - 70

        self.rect.left = SCREEN_WIDTH

    def update(self):
        self.rect.x -= ITEM_SPEED
        if self.rect.right < 0:
            self.kill()


#Функция проверки пересечения с препятствиями
def check_collision_with_obstacles(rect):
    for obstacle in obstacles:
        if rect.colliderect(obstacle.rect):
            return True
    return False


#Группы спрайтов
all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
items = pygame.sprite.Group()
mice = pygame.sprite.Group()
yarn_balls = pygame.sprite.Group()

#Создание кота
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
next_mouse_spawn = random.randint(180, 360)#время появления мыши
font = pygame.font.SysFont('arial', 20)#шрифты
small_font = pygame.font.SysFont('arial', 16)
title_font = pygame.font.SysFont('arial', 36, bold=True)


#Функция отрисовки текста
def draw_text(text, color, x, y, font_obj=font):
    img = font_obj.render(text, True, color) #render() создает изображение с текстом
    screen.blit(img, (x, y)) #blit() рисует изображение текста на основном экране


#Функция сброса игры
def reset_game():
    global score, coins, food, milk, mice_killed, game_over, game_paused, spawn_timer, item_timer, mouse_timer, next_mouse_spawn
    #выводятся очки при окончании игры
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


#Функция для определения позиции текста статистики
def get_stats_position():
    base_x = SCREEN_WIDTH - 150
    test_text = f"Счет: {int(score)}"
    test_surface = font.render(test_text, True, WHITE)
    return base_x


#Главный игровой цикл
running = True
while running:
    clock.tick(FPS) #скорость выполнения игрового цикла.

    for event in pygame.event.get(): #прописываем клавиши
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p or event.key == ord('з') :
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
                elif event.key == pygame.K_b or event.key == ord('и') :
                    current_bg = (current_bg + 1) % len(backgrounds)
            elif (event.key == pygame.K_r or event.key == ord('к')) and game_over:
                reset_game()

    keys = pygame.key.get_pressed() #происходит при зажатии клавиш
    if not keys[pygame.K_DOWN]:
        cat.stand_up()

    if not game_over and not game_paused:
        all_sprites.update()

        bg_x -= BACKGROUND_SPEED #прокрутка фона
        if bg_x <= -SCREEN_WIDTH: #когда фон полностью ушел за левый край
            bg_x = 0 #сбрасываем позицию в начало

        #Спавн(появление) препятствий
        spawn_timer += 1
        if spawn_timer >= 90:
            spawn_timer = 0
            obstacle = Obstacle() #Создание новых препятствий через регулярные промежутки времени(Создает новый экземпляр класса)
            obstacles.add(obstacle) #добавляет в специальную группу для препятствий
            all_sprites.add(obstacle) #добавляет в общую группу всех спрайтов

        #Спавн предметов
        item_timer += 1
        if item_timer >= 45:
            item_timer = 0
            item_type = random.choice(["coin", "fish", "meat", "milk"])

            max_attempts = 10 #10 попыток создать предмет в свободном месте
            for attempt in range(max_attempts):
                item = Item(item_type) #Создает предмет выбранного типа

                if not check_collision_with_obstacles(item.rect): #проверяет, не пересекается ли предмет с существующими препятствиями
                    items.add(item)
                    all_sprites.add(item)
                    break
                else:
                    item.kill()

        #Спавн мышек с разными промежутками на фиксированной низкой высоте
        mouse_timer += 1
        if mouse_timer >= next_mouse_spawn:
            mouse_timer = 0
            next_mouse_spawn = random.randint(180, 480)

            #Мышь появляется на фиксированной НИЗКОЙ высоте
            mouse = Mouse(cat.get_mouse_spawn_height())
            mice.add(mouse)
            all_sprites.add(mouse)

        #Проверка столкновений с препятствиями
        hits = pygame.sprite.spritecollide(cat, obstacles, False)
        for hit in hits:
            if hit.type == "jump" and not cat.is_jumping:
                game_over = True
            elif hit.type == "low_jump" and not cat.is_jumping:
                game_over = True
            elif hit.type == "cloud" and not cat.is_clouding:
                game_over = True

        #Проверка столкновений с мышками
        mouse_hits = pygame.sprite.spritecollide(cat, mice, False) #обнаружение столкновений
        if mouse_hits:
            game_over = True

        #Проверка попадания клубков в мышек
        for yarn_ball in yarn_balls:
            mouse_hits = pygame.sprite.spritecollide(yarn_ball, mice, True) #удаление при столкновении
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

    #Рисуем фоны
    screen.blit(backgrounds[current_bg], (bg_x, 0))
    screen.blit(backgrounds[current_bg], (bg_x + SCREEN_WIDTH, 0))

    #нижняя дощечка
    pygame.draw.rect(screen, BROWN, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
    for i in range(0, SCREEN_WIDTH, 20): #линии
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

    #Отрисовка инструкций
    instructions = [
        "Управление:",
        "ПРОБЕЛ - Высокий прыжок",
        "СТРЕЛКА ВВЕРХ - Низкий прыжок",
        "СТРЕЛКА ВНИЗ - Присесть",
        "СТРЕЛКА ВПРАВО - Выстрел",
        "B - Сменить фон",
        "P - Пауза",
        "R - Перезапуск"
    ]

    for i, instruction in enumerate(instructions):
        draw_text(instruction, text_color, 10, 10 + i * 20, small_font)

    #Экран паузы
    if game_paused and not game_over:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        draw_text("ПАУЗА", WHITE, SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 40, title_font)
        draw_text("Нажми P для продолжения", WHITE, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 10, small_font)

    #Экран Game Over
    if game_over:
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

    pygame.display.flip()

pygame.quit()
sys.exit()