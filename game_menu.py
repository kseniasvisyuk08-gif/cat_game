import pygame
from ui_components import Button, draw_text
from data_manager import save_shop_data
from constants import *


class GameMenu:
    def __init__(self, cat_stand, cat_jump, cat_cloud):
        self.cat_stand = cat_stand
        self.cat_jump = cat_jump
        self.cat_cloud = cat_cloud

        self.active = False
        self.show_instructions = False
        self.show_shop = False
        self.show_search = False
        self.show_selection = False
        self.selection_buttons = []

        # Данные магазина
        self.purchased_items = set()
        self.coins = 0

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

        # Кнопка назад для инструкций
        self.back_button = Button(SCREEN_WIDTH // 2 - 75, 500, 150, 50, "Назад", self.close_instructions)

    def load_data(self, shop_data):
        self.purchased_items = set(shop_data.get("purchased_items", []))
        self.coins = shop_data.get("coins", 0)

    def show_selection_menu(self):
        self.show_selection = True
        self.show_shop = False
        self.show_instructions = False

    def save_shop_state(self, selected_accessory_type):
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
        self.show_selection = False

    def close_shop(self):
        self.show_shop = False

    def close_instructions(self):
        self.show_instructions = False

    def close_selection(self):
        self.show_selection = False
        self.show_shop = True

    def continue_game(self):
        self.active = False
        self.show_selection = False
        self.show_shop = False
        self.show_instructions = False

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
            return True
        else:
            if item in self.purchased_items:
                print(f"{item} уже куплен!")
            else:
                print(f"Недостаточно монет! Нужно {cost}, есть {self.coins}")
            return False

    def select_accessory(self, accessory_type):
        return accessory_type

    def draw(self, surface, selected_accessory_type):
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
            self.draw_selection(surface, selected_accessory_type)
        else:
            self.draw_main_menu(surface)

    def draw_main_menu(self, surface):
        # Заголовок
        title_font = pygame.font.SysFont('arial', 48, bold=True)
        draw_text("МЕНЮ ИГРЫ", WHITE, SCREEN_WIDTH // 2, 100, title_font, center_x=True, center_y=True)

        # Кнопки
        mouse_pos = pygame.mouse.get_pos()
        for button in self.menu_buttons:
            button.check_hover(mouse_pos)
            button.draw(surface)

    def draw_instructions(self, surface):
        # Заголовок
        title_font = pygame.font.SysFont('arial', 40, bold=True)
        draw_text("ИНСТРУКЦИЯ", WHITE, SCREEN_WIDTH // 2, 50, title_font, center_x=True, center_y=True)

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
            text_surf = font.render(line, True, WHITE)
            surface.blit(text_surf, (50, y_offset))
            y_offset += 30

        # Кнопка назад
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.check_hover(mouse_pos)
        self.back_button.draw(surface)

    def draw_shop(self, surface):
        # Заголовок
        title_font = pygame.font.SysFont('arial', 40, bold=True)
        draw_text("МАГАЗИН АКСЕССУАРОВ", WHITE, SCREEN_WIDTH // 2, 50, title_font, center_x=True, center_y=True)

        # Баланс монет
        font = pygame.font.SysFont('arial', 32)
        draw_text(f"Монет: {self.coins}", WHITE, SCREEN_WIDTH // 2, 100, font, center_x=True, center_y=True)

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

    def draw_selection(self, surface, selected_accessory_type):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        title_font = pygame.font.SysFont('arial', 40, bold=True)
        draw_text("ВЫБЕРИТЕ АКСЕССУАР", WHITE, SCREEN_WIDTH // 2, 30, title_font, center_x=True, center_y=True)

        # Собираем все доступные элементы
        available_items = [("Без аксессуара", 0, "none")]

        # Добавляем купленные аксессуары
        if "hat" in self.purchased_items:
            available_items.append(("Шляпа", 1, "hat"))
        if "glasses" in self.purchased_items:
            available_items.append(("Очки", 2, "glasses"))
        if "bow" in self.purchased_items:
            available_items.append(("Бант", 3, "bow"))

        # Если нет купленных аксессуаров
        if len(available_items) <= 1:
            subtitle_font = pygame.font.SysFont('arial', 24)
            draw_text("У вас нет купленных аксессуаров", YELLOW, SCREEN_WIDTH // 2, 100, subtitle_font, center_x=True,
                      center_y=True)

            hint_font = pygame.font.SysFont('arial', 20)
            draw_text("Купите аксессуары в магазине", WHITE, SCREEN_WIDTH // 2, 140, hint_font, center_x=True,
                      center_y=True)

            button_width = 200
            button_height = 50
            button_y = 200

            shop_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, button_y, button_width, button_height)
            pygame.draw.rect(surface, BLUE, shop_rect, border_radius=10)
            pygame.draw.rect(surface, BLACK, shop_rect, 2, border_radius=10)

            shop_font = pygame.font.SysFont('arial', 20)
            shop_text = shop_font.render("Вернуться в магазин", True, WHITE)
            surface.blit(shop_text, (shop_rect.centerx - shop_text.get_width() // 2,
                                     shop_rect.centery - shop_text.get_height() // 2))

            return

        # Если есть купленные аксессуары
        subtitle_font = pygame.font.SysFont('arial', 24)
        draw_text("Какой аксессуар надеть на кота?", WHITE, SCREEN_WIDTH // 2, 90, subtitle_font, center_x=True,
                  center_y=True)

        current_font = pygame.font.SysFont('arial', 22)
        accessory_names = {
            0: "Без аксессуара",
            1: "Шляпа",
            2: "Очки",
            3: "Бант"
        }
        current_text = current_font.render(f"Текущий: {accessory_names[selected_accessory_type]}", True, YELLOW)
        surface.blit(current_text, (SCREEN_WIDTH // 2 - current_text.get_width() // 2, 130))

        card_width = 150
        card_height = 200
        card_margin = 15

        total_width = len(available_items) * card_width + (len(available_items) - 1) * card_margin
        start_x = (SCREEN_WIDTH - total_width) // 2
        y_pos = 180

        # Отображаем все карточки в один ряд
        for i, (name, accessory_id, item_id) in enumerate(available_items):
            card_x = start_x + i * (card_width + card_margin)

            is_selected = (selected_accessory_type == accessory_id)
            card_color = GREEN if is_selected else LIGHT_GRAY

            pygame.draw.rect(surface, card_color, (card_x, y_pos, card_width, card_height), border_radius=10)
            pygame.draw.rect(surface, BLACK, (card_x, y_pos, card_width, card_height), 2, border_radius=10)

            cat_image = self.cat_stand[accessory_id]

            image_width = card_width - 30
            image_height = int(cat_image.get_height() * (image_width / cat_image.get_width()))

            max_image_height = 90
            if image_height > max_image_height:
                image_height = max_image_height
                image_width = int(cat_image.get_width() * (image_height / cat_image.get_height()))

            scaled_cat = pygame.transform.scale(cat_image, (image_width, image_height))

            image_x = card_x + (card_width - image_width) // 2
            image_y = y_pos + 15
            surface.blit(scaled_cat, (image_x, image_y))

            name_font = pygame.font.SysFont('arial', 18, bold=True)
            name_text = name_font.render(name, True, BLACK)
            name_y = image_y + image_height + 15
            surface.blit(name_text, (card_x + card_width // 2 - name_text.get_width() // 2, name_y))

            button_height = 30
            button_y_pos = name_y + 25
            button_rect = pygame.Rect(card_x + 20, button_y_pos, card_width - 40, button_height)
            button_color = GREEN if is_selected else BLUE

            pygame.draw.rect(surface, button_color, button_rect, border_radius=8)
            pygame.draw.rect(surface, BLACK, button_rect, 2, border_radius=8)

            button_text = "Выбрано" if is_selected else "Выбрать"
            btn_font = pygame.font.SysFont('arial', 14)
            btn_text = btn_font.render(button_text, True, WHITE if is_selected else BLACK)
            surface.blit(btn_text, (card_x + card_width // 2 - btn_text.get_width() // 2,
                                    button_y_pos + button_height // 2 - btn_text.get_height() // 2))

        button_width = 180
        button_height = 45
        button_spacing = 20
        button_y = y_pos + card_height + 30

        total_buttons_width = (button_width * 2) + button_spacing
        buttons_start_x = (SCREEN_WIDTH - total_buttons_width) // 2

        # Кнопка "Продолжить"
        continue_rect = pygame.Rect(buttons_start_x, button_y, button_width, button_height)
        pygame.draw.rect(surface, GREEN, continue_rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, continue_rect, 2, border_radius=10)

        continue_font = pygame.font.SysFont('arial', 18)
        continue_text = continue_font.render("Продолжить игру", True, WHITE)
        surface.blit(continue_text, (continue_rect.centerx - continue_text.get_width() // 2,
                                     continue_rect.centery - continue_text.get_height() // 2))

        # Кнопка "В магазин"
        shop_rect = pygame.Rect(buttons_start_x + button_width + button_spacing, button_y,
                                button_width, button_height)
        pygame.draw.rect(surface, BLUE, shop_rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, shop_rect, 2, border_radius=10)

        shop_font = pygame.font.SysFont('arial', 18)
        shop_text = shop_font.render("Вернуться в магазин", True, WHITE)
        surface.blit(shop_text, (shop_rect.centerx - shop_text.get_width() // 2,
                                 shop_rect.centery - shop_text.get_height() // 2))