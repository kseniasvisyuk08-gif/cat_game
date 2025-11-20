import pygame

# Инициализация Pygame
pygame.init() #инициализируем библиотеку, чтобы использовать функции

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = 1
JUMP_STRENGTH = 19.8
LOW_JUMP_STRENGTH = 15

#Загрузка изображения name
def load_image(name, scale=1):
    image = pygame.image.load(name) #загрузка изображения по заданному пути
    if scale != 1:
        new_size = (int(image.get_width() * scale), int(image.get_height() * scale)) #get_width/get_height-функции из pygame
        image = pygame.transform.scale(image, new_size) #меняет масштаб изображения на заданный в предыдущей строке
    return image.convert_alpha() #заменяем прозрачные пиксели на черный

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

    def is_standing(self):
        # Проверяет, стоит ли кот нормально (не прыгает и не приседает)
        return not self.is_jumping and not self.is_clouding and self.rect.bottom == self.ground_level

    def get_mouse_spawn_height(self):
        # Возвращает фиксированную высоту для появления мышей (НИЖЕ)
        return self.mouse_spawn_height
