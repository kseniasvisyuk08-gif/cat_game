import pygame

# Инициализация Pygame
pygame.init()  # инициализируем библиотеку, чтобы использовать функции

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = 1
JUMP_STRENGTH = 19.8
LOW_JUMP_STRENGTH = 15
MOUSE_SPEED = 5
BALL_SPEED = 10
GRAY = (128, 128, 128)
PINK = (255, 182, 193)
BLACK = (0, 0, 0)

# Создание окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # задаем размеры экрана
pygame.display.set_caption("Бегущий кот")  # задает название игры(сверху)
clock = pygame.time.Clock()


# Загрузка изображения name
def load_image(name, scale=1):
    image = pygame.image.load(name)  # загрузка изображения по заданному пути
    if scale != 1:
        new_size = (int(image.get_width() * scale),
                    int(image.get_height() * scale))  # get_width/get_height-функции из pygame
        image = pygame.transform.scale(image, new_size)  # меняет масштаб изображения на заданный в предыдущей строке
    return image.convert_alpha()  # заменяем прозрачные пиксели на черный


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


# выстрел
class Ball(pygame.sprite.Sprite):  # pygame.sprite.Sprite-класс в pygame, который работает с спрайтами для 2d-графики
    def __init__(self, x, y):
        super().__init__()  # метод, соединяющий pygame.sprite.Sprite
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)  # создаем поле под шар
        # Рисуем шар
        pygame.draw.circle(self.image, (128, 128, 128), (14, 14), 14)

        self.rect = self.image.get_rect()  # создаем прямоугольное пространство, под мяч
        self.rect.centerx = x  # задаем центр мяча
        self.rect.centery = y
        self.speed = BALL_SPEED  # задаем скорость движения шара

    # перемещение шара
    def update(self):
        self.rect.x += self.speed
        if self.rect.left > SCREEN_WIDTH:  # проверка на выход шара за правую границу
            self.kill()


# Спрайты кота
class Cat(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # задаем спрайты  на все состояния кота
        self.run_frames_right = cat_run_frames
        self.jump_frame_right = cat_jump
        self.stand_frame_right = cat_stand
        self.cloud_frame_right = cat_cloud

        self.current_frame = 0
        self.image = self.run_frames_right[self.current_frame]  # отображение текущнго спрайта через массив спрайтов
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

        # проверка находится ли кот на земле
        if self.rect.bottom > self.ground_level:
            self.rect.bottom = self.ground_level
            self.velocity_y = 0
            self.is_jumping = False

        # Плавная смена анимации
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.run_frames_right)

            # смена картинок при различных действиях
            if self.is_jumping:
                self.image = self.jump_frame_right
            elif self.is_clouding:
                self.image = self.cloud_frame_right
            else:
                self.image = self.run_frames_right[self.current_frame]

        # кулдаун стрельбы, чтобы между выстрелами были промежутки
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


# Мышь (враг)
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


