import pygame
import random
import sys
import json
import os
import atexit  # Добавляем модуль для регистрации функций при выходе


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


# Глобальная переменная для рекорда
global_high_score = 0
global_money_score = 0
score_updated = False  # Флаг, что рекорд обновлен и нужно сохранить
new_record_achieved = False  # Флаг, что достигнут новый рекорд
money_updated = False
HIGH_SCORE_FILE = "high_score.json"
MONEY_SCORE_FILE= "money_score.json"
SHOP_DATA_FILE = "shop.json"


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

#Создание окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) #задаем размеры экрана
pygame.display.set_caption("Бегущий кот") #задает название игры(сверху)
clock = pygame.time.Clock()


# Функции для работы с рекордом
def load_high_score():
    global global_high_score

    if not os.path.exists(HIGH_SCORE_FILE):
        global_high_score = 0
        return 0

    file = open(HIGH_SCORE_FILE, 'r', encoding='utf-8')
    content = file.read()
    file.close()

    if not content.strip():
        global_high_score = 0
        return 0

    data = json.loads(content)

    if isinstance(data, dict) and "high_score" in data:
        global_high_score = data["high_score"]
        return global_high_score

    global_high_score = 0
    return 0

def load_money_score():
    global global_money_score
    if not os.path.exists(MONEY_SCORE_FILE):
        global_money_score = 0
        return 0
    file = open(MONEY_SCORE_FILE, 'r', encoding='utf-8')
    content = file.read()
    file.close()

    if not content.strip():
        global_money_score = 0
        return 0
    data=json.loads(content)

    if isinstance(data, dict) and "money_score" in data:
        global_money_score = data["money_score"]
        return global_money_score

    global_money_score =0
    return 0

def save_high_score():
    global global_high_score, score_updated

    if not score_updated:
        return

    data = {"high_score": int(global_high_score)}
    file = open(HIGH_SCORE_FILE, 'w', encoding='utf-8')
    json.dump(data, file, ensure_ascii=False, indent=4)
    file.close()

    score_updated = False

def save_money_score():
    global global_money_score, money_updated

    if not money_updated:
        return
    data={"money_score": int(global_money_score)}
    file= open(MONEY_SCORE_FILE, 'w', encoding='utf-8')
    json.dump(data, file, ensure_ascii=False, indent=4)
    file.close()

    money_updated = False

def update_high_score(new_score):
    global global_high_score, score_updated, new_record_achieved

    if new_score > global_high_score:
        global_high_score = int(new_score)
        score_updated = True
        new_record_achieved = True
        save_high_score()

    return global_high_score

def update_money_score(new_money_score):
    global global_money_score, money_updated

    global_money_score = int(new_money_score)
    money_updated=True
    save_money_score()

    return global_money_score


def load_shop_data():
    if not os.path.exists(SHOP_DATA_FILE):
        initial_data = {
            "purchased_items": [],
            "coins": 0,
            "selected_accessory": 0
        }
        save_shop_data(initial_data)
        return initial_data

    file = open(SHOP_DATA_FILE, 'r', encoding='utf-8')
    content = file.read()
    file.close()

    if not content.strip():
        data = {
            "purchased_items": [],
            "coins": 0,
            "selected_accessory": 0
        }
        return data

    data = json.loads(content)

    if not isinstance(data, dict):
        data = {
            "purchased_items": [],
            "coins": 0,
            "selected_accessory": 0
        }
    else:
        if "purchased_items" not in data:
            data["purchased_items"] = []
        if "coins" not in data:
            data["coins"] = 0
        if "selected_accessory" not in data:
            data["selected_accessory"] = 0

    return data


def save_shop_data(data):
    file = open(SHOP_DATA_FILE, 'w', encoding='utf-8')
    json.dump(data, file, ensure_ascii=False, indent=4)
    file.close()
    return True


def save_game_state():
    # Сохраняем данные магазина из меню
    shop_data = {
        "purchased_items": list(game_menu.purchased_items),
        "coins": game_menu.coins,
        "selected_accessory": selected_accessory_type
    }
    save_shop_data(shop_data)

    # Сохраняем рекорды
    save_high_score()
    save_money_score()


# Регистрируем общую функцию сохранения
atexit.register(save_game_state)

# Регистрируем функцию сохранения при выходе из программы
atexit.register(save_high_score)
atexit.register(save_money_score)

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

#переменная для выбранного аксесуара(0-нет ничего, 1-шляпа,2-очки,3-бант)
selected_accessory_type = 0

#Загрузка спрайтов кота
cat_stand0 = load_image("cat1.png", 1.6)
cat_jump0 = load_image("cat2.png", 1.6)
cat_cloud0 = load_image("cat3.png", 1.2)

cat_stand1 = load_image("cathat1.png", 1.6)
cat_jump1 = load_image("cathat2.png", 1.6)
cat_cloud1 = load_image("cathat3.png", 1.2)

cat_stand2 = load_image("catglasses1.png", 1.6)
cat_jump2 = load_image("catglasses2.png", 1.6)
cat_cloud2 = load_image("catglasses3.png", 1.2)

cat_stand3 = load_image("catbow1.png", 1.6)
cat_jump3 = load_image("catbow2.png", 1.6)
cat_cloud3 = load_image("catbow3.png", 1.2)

cat_stand=[cat_stand0,cat_stand1,cat_stand2,cat_stand3]
cat_jump=[cat_jump0,cat_jump1,cat_jump2,cat_jump3]
cat_cloud=[cat_cloud0,cat_cloud1,cat_cloud2,cat_cloud3]


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
        self.show_search = False
        self.show_selection = False
        self.selection_buttons = []

        button_width = 180
        button_height = 60
        button_margin = 20
        total_width = (button_width * 3) + (button_margin * 2)
        start_x = (SCREEN_WIDTH - total_width) // 2

        shop_data = load_shop_data()
        self.purchased_items = set(shop_data["purchased_items"])
        self.coins = shop_data["coins"]

        global selected_accessory_type
        selected_accessory_type = shop_data.get("selected_accessory", 0)

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
            Button(650, 500, 150, 50, "Выбрать", self.show_selection_menu),
            Button(SCREEN_WIDTH // 2 - 75, 550, 150, 50, "Продолжить игру", self.continue_game_from_shop)
        ]

        #Кнопки выбора акссесуара
        self.selection_buttons = [
            Button(start_x, 200, button_width, button_height,
                   "Шляпа", lambda: self.select_accessory(1)),
            Button(start_x + button_width + button_margin, 200,
                   button_width, button_height, "Очки",
                   lambda: self.select_accessory(2)),
            Button(start_x + (button_width + button_margin) * 2, 200,
                   button_width, button_height, "Бант",
                   lambda: self.select_accessory(3)),
            Button(SCREEN_WIDTH // 2 - 75, 300, 150, 50,
                   "Назад", self.close_selection)
        ]


        # Кнопка назад для инструкций
        self.back_button = Button(SCREEN_WIDTH // 2 - 75, 500, 150, 50, "Назад", self.close_instructions)

    def show_selection_menu(self):
        if len(self.purchased_items) > 0:
            self.show_selection = True
            self.show_shop = False
        else:
            print("Сначала купите хотя бы один аксессуар!")

    def save_shop_state(self):
        shop_data = {
            "purchased_items": list(self.purchased_items),
            "coins": self.coins,
            "selected_accessory": selected_accessory_type
        }
        save_shop_data(shop_data)

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

    def  close_selection(self):
        self.show_selection = False
        self.show_shop = True

    def continue_game(self):
        self.active = False
        self.show_selection = False
        self.show_shop = False
        self.show_instructions = False
        self.save_shop_state()

    def continue_game_from_shop(self):
        self.continue_game()

    def back_to_shop(self):
        self.show_selection = False
        self.show_shop = True

    def buy_item(self, item, cost):
        if self.coins >= cost and item not in self.purchased_items:
            self.coins -= cost
            self.purchased_items.add(item)
            print(f"Куплен {item} за {cost} монет")

            global total_coins, current_coins
            total_coins = self.coins - current_coins
            update_money_score(self.coins)

            self.save_shop_state()

            # Сразу показываем меню выбора после покупки
            if len(self.purchased_items) > 0:
                self.show_selection = True
                self.show_shop = False
        else:
            if item in self.purchased_items:
                print(f"{item} уже куплен!")
            else:
                print(f"Недостаточно монет! Нужно {cost}, есть {self.coins}")

    def select_accessory(self, accessory_type):
        global selected_accessory_type, cat
        selected_accessory_type = accessory_type
        print(f"Выбран аксессуар: {accessory_type}")

        cat.update_sprites()

        self.save_shop_state()
        self.close_selection()

    def draw(self, surface):
        if not self.active:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        if self.show_instructions:
            self.draw_instructions(surface)
        elif self.show_shop:
            self.draw_shop(surface)
        elif self.show_selection:
            self.draw_selection(surface)
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
            pygame.draw.rect(surface, LIGHT_GRAY, (100, y_offset, 600, 80), border_radius=10)
            pygame.draw.rect(surface, DARK_GRAY, (100, y_offset, 600, 80), 2, border_radius=10)

            name_text = item_font.render(name, True, BLACK)
            surface.blit(name_text, (120, y_offset + 10))

            desc_font = pygame.font.SysFont('arial', 18)
            desc_text = desc_font.render(description, True, DARK_GRAY)
            surface.blit(desc_text, (120, y_offset + 40))

            price_text = item_font.render(price, True, GRAY if item_id not in self.purchased_items else GREEN)
            surface.blit(price_text, (600, y_offset + 30))

            status_font = pygame.font.SysFont('arial', 18)
            if item_id in self.purchased_items:
                status_text = status_font.render("Куплено", True, GREEN)
                surface.blit(status_text, (620, y_offset + 55))

            y_offset += 100

        mouse_pos = pygame.mouse.get_pos()
        for i in range(4):
            self.shop_buttons[i].rect.y = 500
            self.shop_buttons[i].check_hover(mouse_pos)
            self.shop_buttons[i].draw(surface)
        self.shop_buttons[4].rect.y = 550
        self.shop_buttons[4].check_hover(mouse_pos)
        self.shop_buttons[4].draw(surface)

    def draw_selection(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        title_font = pygame.font.SysFont('arial', 40, bold=True)
        title = title_font.render("ВЫБЕРИТЕ АКСЕССУАР", True, WHITE)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        subtitle_font = pygame.font.SysFont('arial', 24)
        subtitle = subtitle_font.render("Какой аксессуар надеть на кота?", True, WHITE)
        surface.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 90))

        current_font = pygame.font.SysFont('arial', 22)
        accessory_names = {
            0: "Без аксессуара",
            1: "Шляпа",
            2: "Очки",
            3: "Бант"
        }
        current_text = current_font.render(f"Текущий: {accessory_names[selected_accessory_type]}", True, YELLOW)
        surface.blit(current_text, (SCREEN_WIDTH // 2 - current_text.get_width() // 2, 130))

        available_items = []
        if "hat" in self.purchased_items:
            available_items.append(("Шляпа", 1, "hat"))
        if "glasses" in self.purchased_items:
            available_items.append(("Очки", 2, "glasses"))
        if "bow" in self.purchased_items:
            available_items.append(("Бант", 3, "bow"))

        # Всегда показываем "Без аксессуара" как доступный вариант
        all_items = [("Без аксессуара", 0, "none")] + available_items

        # Определяем позицию для кнопок управления
        button_y = 500  # Позиция для кнопок управления

        if len(all_items) == 1:  # Только "Без аксессуара"
            card_width = 250
            card_height = 280
            card_x = (SCREEN_WIDTH - card_width) // 2
            card_y = 200

            # Рисуем карточку "Без аксессуара"
            card_color = GREEN if selected_accessory_type == 0 else LIGHT_GRAY
            pygame.draw.rect(surface, card_color, (card_x, card_y, card_width, card_height), border_radius=15)
            pygame.draw.rect(surface, BLACK, (card_x, card_y, card_width, card_height), 3, border_radius=15)

            # Картинка кота без аксессуара
            cat_no_acc = cat_stand[0]
            image_width = card_width - 50
            image_height = int(cat_no_acc.get_height() * (image_width / cat_no_acc.get_width()))
            scaled_cat_no_acc = pygame.transform.scale(cat_no_acc, (image_width, image_height))

            image_x = card_x + (card_width - image_width) // 2
            image_y = card_y + 20
            surface.blit(scaled_cat_no_acc, (image_x, image_y))

            # Название ПОД картинкой
            name_font = pygame.font.SysFont('arial', 22, bold=True)
            name_text = name_font.render("Без аксессуара", True, BLACK)
            surface.blit(name_text, (card_x + card_width // 2 - name_text.get_width() // 2,
                                     image_y + image_height + 15))

            # Кнопка выбора ПОД названием
            button_rect = pygame.Rect(card_x + 50, card_y + card_height - 60, card_width - 100, 40)
            button_color = GREEN if selected_accessory_type == 0 else LIGHT_GRAY
            pygame.draw.rect(surface, button_color, button_rect, border_radius=8)
            pygame.draw.rect(surface, BLACK, button_rect, 2, border_radius=8)

            button_text = "Выбрано" if selected_accessory_type == 0 else "Выбрать"
            btn_font = pygame.font.SysFont('arial', 18)
            btn_text = btn_font.render(button_text, True, BLACK)
            surface.blit(btn_text, (card_x + card_width // 2 - btn_text.get_width() // 2,
                                    card_y + card_height - 45))

            button_y = 500  # Кнопки управления ниже
        else:
            # Есть аксессуары - показываем все карточки
            card_width = 200
            card_height = 250  # Увеличили высоту для карточки
            card_margin = 20

            # Рассчитываем сколько карточек поместится в ряд
            max_cards_per_row = 3
            cards_in_row = min(len(all_items), max_cards_per_row)
            total_width = cards_in_row * card_width + (cards_in_row - 1) * card_margin
            start_x = (SCREEN_WIDTH - total_width) // 2

            # Распределяем карточки по рядам
            rows = []
            current_row = []
            for item in all_items:
                current_row.append(item)
                if len(current_row) == max_cards_per_row:
                    rows.append(current_row)
                    current_row = []
            if current_row:
                rows.append(current_row)

            # Отображаем карточки
            y_pos = 180
            for row in rows:
                row_width = len(row) * card_width + (len(row) - 1) * card_margin
                row_start_x = (SCREEN_WIDTH - row_width) // 2

                for i, (name, accessory_id, item_id) in enumerate(row):
                    card_x = row_start_x + i * (card_width + card_margin)

                    # Цвет карточки
                    card_color = GREEN if selected_accessory_type == accessory_id else LIGHT_GRAY
                    pygame.draw.rect(surface, card_color, (card_x, y_pos, card_width, card_height), border_radius=15)
                    pygame.draw.rect(surface, BLACK, (card_x, y_pos, card_width, card_height), 3, border_radius=15)

                    # Картинка кота
                    cat_image = cat_stand[accessory_id]
                    image_width = card_width - 40
                    image_height = int(cat_image.get_height() * (image_width / cat_image.get_width()))

                    # Если картинка слишком высокая, уменьшаем
                    max_image_height = 150
                    if image_height > max_image_height:
                        image_height = max_image_height
                        image_width = int(cat_image.get_width() * (image_height / cat_image.get_height()))

                    scaled_cat = pygame.transform.scale(cat_image, (image_width, image_height))

                    image_x = card_x + (card_width - image_width) // 2
                    image_y = y_pos + 20
                    surface.blit(scaled_cat, (image_x, image_y))

                    # Название аксессуара ПОД картинкой
                    name_font = pygame.font.SysFont('arial', 20, bold=True)
                    name_text = name_font.render(name, True, BLACK)
                    surface.blit(name_text, (card_x + card_width // 2 - name_text.get_width() // 2,
                                             image_y + image_height + 15))

                    # Кнопка выбора ПОД названием
                    button_rect = pygame.Rect(card_x + 30, y_pos + card_height - 50, card_width - 60, 35)
                    button_color = GREEN if selected_accessory_type == accessory_id else LIGHT_GRAY
                    pygame.draw.rect(surface, button_color, button_rect, border_radius=8)
                    pygame.draw.rect(surface, BLACK, button_rect, 2, border_radius=8)

                    button_text = "Выбрано" if selected_accessory_type == accessory_id else "Выбрать"
                    btn_font = pygame.font.SysFont('arial', 16)
                    btn_text = btn_font.render(button_text, True, BLACK)
                    surface.blit(btn_text, (card_x + card_width // 2 - btn_text.get_width() // 2,
                                            y_pos + card_height - 40))

                y_pos += card_height + 30  # Переход на следующий ряд

            button_y = y_pos + 20  # Кнопки управления после последнего ряда

        # Кнопки управления внизу экрана
        button_width = 200
        button_height = 50
        button_spacing = 30

        # Рассчитываем позиции для двух кнопок
        total_buttons_width = (button_width * 2) + button_spacing
        buttons_start_x = (SCREEN_WIDTH - total_buttons_width) // 2

        # Кнопка "Продолжить"
        continue_rect = pygame.Rect(buttons_start_x, button_y, button_width, button_height)
        pygame.draw.rect(surface, GREEN, continue_rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, continue_rect, 2, border_radius=10)

        continue_font = pygame.font.SysFont('arial', 20)
        continue_text = continue_font.render("Продолжить игру", True, WHITE)
        surface.blit(continue_text, (continue_rect.centerx - continue_text.get_width() // 2,
                                     continue_rect.centery - continue_text.get_height() // 2))

        # Кнопка "В магазин"
        shop_rect = pygame.Rect(buttons_start_x + button_width + button_spacing, button_y, button_width, button_height)
        pygame.draw.rect(surface, BLUE, shop_rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, shop_rect, 2, border_radius=10)

        shop_font = pygame.font.SysFont('arial', 20)
        shop_text = shop_font.render("Вернуться в магазин", True, WHITE)
        surface.blit(shop_text, (shop_rect.centerx - shop_text.get_width() // 2,
                                 shop_rect.centery - shop_text.get_height() // 2))

        # Обработка кликов
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        if mouse_pressed:
            # Обработка кликов по карточкам (будет в основном цикле)
            pass

game_menu = GameMenu()


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

        self.update_sprites()

        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT - 100)

    def update_sprites(self):
        global selected_accessory_type
        self.stand_frame_right = cat_stand[selected_accessory_type]
        self.jump_frame_right = cat_jump[selected_accessory_type]
        self.cloud_frame_right = cat_cloud[selected_accessory_type]
        self.run_frames_right = []
        for i in range(2):
            frame = self.stand_frame_right.copy()
            if i % 2 == 0:
                frame = pygame.transform.scale(frame,(int(frame.get_width() * 0.9), int(frame.get_height() * 0.95)))
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
cat.update_sprites()

# Переменные игры
score = 0
current_coins = 0
total_coins = load_money_score()
food = 0
milk = 0
mice_killed = 0
high_score = load_high_score()
game_over = False
game_paused = False
spawn_timer = 0
item_timer = 0
mouse_timer = 0
next_mouse_spawn = random.randint(180, 360)#время появления мыши
font = pygame.font.SysFont('arial', 20)#шрифты
small_font = pygame.font.SysFont('arial', 16)
title_font = pygame.font.SysFont('arial', 36, bold=True)
record_font = pygame.font.SysFont('arial', 42, bold=True)


def draw_text(text, color, x, y, font_obj=font, center_x=False, center_y=False):
    img = font_obj.render(text, True, color)
    if center_x or center_y:
        rect = img.get_rect()
        if center_x:
            rect.centerx = x
        else:
            rect.x = x
        if center_y:
            rect.centery = y
        else:
            rect.y = y
        screen.blit(img, rect)
    else:
        screen.blit(img, (x, y))


#Функция сброса игры
def reset_game():
    global score, current_coins, food, milk, mice_killed, game_over, game_paused, spawn_timer, item_timer, mouse_timer, next_mouse_spawn, new_record_achieved
    for sprite in all_sprites:
        if sprite != cat:
            sprite.kill()

    score = 0
    current_coins = 0
    food = 0
    milk = 0
    mice_killed = 0
    game_over = False
    game_paused = False
    spawn_timer = 0
    item_timer = 0
    mouse_timer = 0
    next_mouse_spawn = random.randint(180, 360)
    new_record_achieved = False

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
    # Обновляем количество монет в меню
    game_menu.coins = total_coins + current_coins

    for event in pygame.event.get(): #прописываем клавиши
        if event.type == pygame.QUIT:
            update_high_score(score)
            save_high_score()
            update_money_score(total_coins + current_coins)
            save_money_score()
            running = False


        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # Enter
                if not game_over:
                    game_menu.active = not game_menu.active
                    if game_menu.active:
                        game_paused = True
                    else:
                        # Если закрываем меню, сбрасываем все подменю
                        game_menu.show_instructions = False
                        game_menu.show_shop = False
                        game_menu.show_selection = False
                        # Возвращаемся в игру (убираем паузу)
                        game_paused = False
                        game_menu.save_shop_state()

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
                    elif event.key == pygame.K_b or event.key == ord('и') :
                        current_bg = (current_bg + 1) % len(backgrounds)
                elif (event.key == pygame.K_r or event.key == ord('к')) and game_over:
                    reset_game()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                if game_menu.active:
                    if game_menu.show_instructions:
                        game_menu.back_button.check_click(mouse_pos)
                    elif game_menu.show_shop:
                        for button in game_menu.shop_buttons:
                            button.check_click(mouse_pos)
                    elif game_menu.show_selection:
                        if event.button == 1:
                            mouse_pos = pygame.mouse.get_pos()

                            button_width = 200
                            button_height = 50
                            button_spacing = 30
                            button_y = 500

                            available_items = []
                            if "hat" in game_menu.purchased_items:
                                available_items.append(("Шляпа", 1, "hat"))
                            if "glasses" in game_menu.purchased_items:
                                available_items.append(("Очки", 2, "glasses"))
                            if "bow" in game_menu.purchased_items:
                                available_items.append(("Бант", 3, "bow"))

                            all_items = [("Без аксессуара", 0, "none")] + available_items

                            if len(all_items) > 1:
                                card_height = 250
                                rows = (len(all_items) + 2) // 3  # Округление вверх
                                button_y = 180 + rows * (card_height + 30) + 20

                            total_buttons_width = (button_width * 2) + button_spacing
                            buttons_start_x = (SCREEN_WIDTH - total_buttons_width) // 2

                            continue_rect = pygame.Rect(buttons_start_x, button_y, button_width, button_height)
                            shop_rect = pygame.Rect(buttons_start_x + button_width + button_spacing, button_y,
                                                        button_width, button_height)

                            if continue_rect.collidepoint(mouse_pos):
                                game_menu.continue_game()

                            elif shop_rect.collidepoint(mouse_pos):
                                game_menu.back_to_shop()

                            all_items = [("Без аксессуара", 0, "none")]
                            if "hat" in game_menu.purchased_items:
                                all_items.append(("Шляпа", 1, "hat"))
                            if "glasses" in game_menu.purchased_items:
                                all_items.append(("Очки", 2, "glasses"))
                            if "bow" in game_menu.purchased_items:
                                all_items.append(("Бант", 3, "bow"))

                            card_width = 200
                            card_height = 250
                            card_margin = 20
                            max_cards_per_row = 3

                            rows = []
                            current_row = []
                            for item in all_items:
                                current_row.append(item)
                                if len(current_row) == max_cards_per_row:
                                    rows.append(current_row)
                                    current_row = []
                            if current_row:
                                rows.append(current_row)

                            y_pos = 180
                            for row in rows:
                                row_width = len(row) * card_width + (len(row) - 1) * card_margin
                                row_start_x = (SCREEN_WIDTH - row_width) // 2

                                for i, (name, accessory_id, item_id) in enumerate(row):
                                    card_x = row_start_x + i * (card_width + card_margin)
                                    card_rect = pygame.Rect(card_x, y_pos, card_width, card_height)
                                    if card_rect.collidepoint(mouse_pos):
                                        game_menu.select_accessory(accessory_id)

                                y_pos += card_height + 30

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
        elif game_menu.show_selection:
            if hasattr(game_menu, 'remove_button') and selected_accessory_type > 0:
                game_menu.remove_button.check_hover(mouse_pos)
            if hasattr(game_menu, 'back_selection_button'):
                game_menu.back_selection_button.check_hover(mouse_pos)
            if hasattr(game_menu, 'current_selection_buttons'):
                for button in game_menu.current_selection_buttons:
                    button.check_hover(mouse_pos)
        else:
            for button in game_menu.menu_buttons:
                button.check_hover(mouse_pos)

    keys = pygame.key.get_pressed() #происходит при зажатии клавиш
    if not keys[pygame.K_DOWN]:
        cat.stand_up()

    if not game_over and not game_paused and not game_menu.active:
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
                update_high_score(score)
            elif hit.type == "low_jump" and not cat.is_jumping:
                game_over = True
                update_high_score(score)
            elif hit.type == "cloud" and not cat.is_clouding:
                game_over = True
                update_high_score(score)

        #Проверка столкновений с мышками
        mouse_hits = pygame.sprite.spritecollide(cat, mice, False) #обнаружение столкновений
        if mouse_hits:
            game_over = True
            update_high_score(score)

        #Проверка попадания клубков в мышек
        for yarn_ball in yarn_balls:
            mouse_hits = pygame.sprite.spritecollide(yarn_ball, mice, True) #удаление при столкновении
            for mouse in mouse_hits:
                yarn_ball.kill()
                mice_killed += 1
                score += 50
                update_high_score(score)

        # Проверка сбора предметов
        collected = pygame.sprite.spritecollide(cat, items, True)
        for item in collected:
            if item.type == "coin":
                current_coins += 1
                score += 10
                update_money_score(total_coins+current_coins)
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
        update_high_score(score)

        update_money_score(total_coins+current_coins)

    #Рисуем фоны
    screen.blit(backgrounds[current_bg], (bg_x, 0))
    screen.blit(backgrounds[current_bg], (bg_x + SCREEN_WIDTH, 0))

    #нижняя дощечка
    pygame.draw.rect(screen, BROWN, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
    for i in range(0, SCREEN_WIDTH, 20): #линии
        pygame.draw.line(screen, (110, 60, 30), (i, SCREEN_HEIGHT - 50), (i, SCREEN_HEIGHT), 1)

    all_sprites.draw(screen)

    text_color = get_text_color()
    stats_x = SCREEN_WIDTH - 180  # Немного левее для лучшего выравнивания
    stats_start_y = 20
    stats_spacing = 25

    # Отрисовка статистики
    draw_text(f"Рекорд: {int(high_score)}", text_color, stats_x, stats_start_y)
    draw_text(f"Монеты: {total_coins + current_coins}", text_color, stats_x, stats_start_y + stats_spacing)
    draw_text(f"Еда: {food}", text_color, stats_x, stats_start_y + stats_spacing * 2)
    draw_text(f"Молоко: {milk}", text_color, stats_x, stats_start_y + stats_spacing * 3)
    draw_text(f"Мыши: {mice_killed}", text_color, stats_x, stats_start_y + stats_spacing * 4)
    draw_text(f"Счет: {int(score)}", text_color, stats_x, stats_start_y + stats_spacing * 5)

    instructions_left_x = 15  # Отступ слева
    instructions_start_y = 20
    instructions_spacing = 22  # Интервал между

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

    # Рисуем инструкции с учетом пустых строк
    current_y = instructions_start_y
    for instruction in instructions:
        if instruction:  # Если строка не пустая
            draw_text(instruction, text_color, instructions_left_x, current_y, small_font)
        current_y += instructions_spacing

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

        # Центральные координаты для всего экрана Game Over
        center_x = SCREEN_WIDTH // 2
        game_over_start_y = 120  # Начинаем выше

        # Отображение нового рекорда, если он достигнут
        if new_record_achieved:
            # Золотая рамка для нового рекорда
            pygame.draw.rect(screen, GOLD, (center_x - 220, game_over_start_y - 20, 440, 70), 4, border_radius=12)
            pygame.draw.rect(screen, (30, 30, 30, 220), (center_x - 216, game_over_start_y - 16, 432, 62),
                             border_radius=10)

            # Текст нового рекорда
            draw_text("НОВЫЙ РЕКОРД!", GOLD, center_x, game_over_start_y + 15, record_font, center_x=True,
                      center_y=True)
            game_over_start_y += 90  # Сдвигаем остальное содержимое ниже
        else:
            game_over_start_y += 20

        draw_text("GAME OVER", RED, center_x, game_over_start_y, title_font, center_x=True, center_y=True)
        # Статистика Game Over - центрированная колонка
        stats_start_y = game_over_start_y + 60
        stat_spacing = 35

        stats_items = [
            f"Финальный счет: {int(score)}",
            f"Собрано монет: {total_coins + current_coins}",
            f"Собрано еды: {food}",
            f"Собрано молока: {milk}",
            f"Убито мышек: {mice_killed}"
        ]

        for i, stat in enumerate(stats_items):
            draw_text(stat, WHITE, center_x, stats_start_y + i * stat_spacing, font, center_x=True, center_y=True)

        # Инструкция для перезапуска
        restart_y = stats_start_y + len(stats_items) * stat_spacing + 30
        draw_text("Нажми R для перезапуска", WHITE, center_x, restart_y, small_font, center_x=True, center_y=True)
    # Отрисовка меню
    game_menu.draw(screen)
    pygame.display.flip()

save_high_score(high_score)
save_money_score(total_coins+current_coins)
save_game_state()
pygame.quit()
sys.exit()