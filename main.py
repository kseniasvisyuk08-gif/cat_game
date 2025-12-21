import pygame
import sys
import random
from typing import List, Dict, Tuple, Optional, Any, Set, Final
from constants import *
from data_manager import *
from ui_components import *
from game_objects import *
from game_menu import GameMenu


def main() -> None:
    """Инициализация"""
    screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Бегущий кот")
    clock: pygame.time.Clock = pygame.time.Clock()

    """Загрузка данных"""
    load_high_score()
    load_money_score()
    shop_data: Dict[str, Any] = load_shop_data()
    selected_accessory_type: int = shop_data.get("selected_accessory", 0)

    """Загрузка фонов"""
    backgrounds: List[pygame.Surface] = []
    for i in range(1, 5):
        bg: pygame.Surface = load_image(f"fon{i}.png")
        if bg.get_width() != SCREEN_WIDTH or bg.get_height() != SCREEN_HEIGHT:
            bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        backgrounds.append(bg)

    current_bg: int = 0
    bg_x: int = 0

    """Музыка"""
    pygame.mixer.init()
    pygame.mixer.music.load("music1.mp3")
    pygame.mixer.music.play(-1)

    """Загрузка спрайтов кота"""
    cat_stand: List[pygame.Surface] = [
        load_image("cat1.png", 1.6),
        load_image("cathat1.png", 1.6),
        load_image("catglasses1.png", 1.6),
        load_image("catbow1.png", 1.6)
    ]

    cat_jump: List[pygame.Surface] = [
        load_image("cat2.png", 1.6),
        load_image("cathat2.png", 1.6),
        load_image("catglasses2.png", 1.6),
        load_image("catbow2.png", 1.6)
    ]

    cat_cloud: List[pygame.Surface] = [
        load_image("cat3.png", 1.2),
        load_image("cathat3.png", 1.2),
        load_image("catglasses3.png", 1.2),
        load_image("catbow3.png", 1.2)
    ]

    """Загрузка препятствий"""
    pregrada_images: List[pygame.Surface] = []
    pregrada_types: List[str] = []

    for i in range(1, 4):
        pregrada: pygame.Surface
        if i == 2:
            pregrada = load_image(f"pregrada{i}.png", 0.3)
            pregrada_types.append("low_jump")
        elif i == 3:
            pregrada = load_image(f"pregrada{i}.png", 1.2)
            pregrada_types.append("cloud")
        else:
            pregrada = load_image(f"pregrada{i}.png", 0.2)
            pregrada_types.append("jump")
        pregrada_images.append(pregrada)

    """Создание меню"""
    game_menu: GameMenu = GameMenu(cat_stand, cat_jump, cat_cloud)
    game_menu.load_data(shop_data)
    game_menu.coins = global_money_score

    """Создание кота"""
    cat: Cat = Cat(cat_stand, cat_jump, cat_cloud, selected_accessory_type)

    """Группы спрайтов"""
    all_sprites: pygame.sprite.Group = pygame.sprite.Group()
    obstacles: pygame.sprite.Group = pygame.sprite.Group()
    items: pygame.sprite.Group = pygame.sprite.Group()
    mice: pygame.sprite.Group = pygame.sprite.Group()
    yarn_balls: pygame.sprite.Group = pygame.sprite.Group()

    all_sprites.add(cat)

    """Переменные игры"""
    score: float = 0.0
    current_coins: int = 0
    total_coins: int = global_money_score
    food: int = 0
    milk: int = 0
    mice_killed: int = 0
    high_score: float = float(global_high_score)
    game_over: bool = False
    game_paused: bool = False
    spawn_timer: int = 0
    item_timer: int = 0
    mouse_timer: int = 0
    next_mouse_spawn: int = random.randint(180, 360)

    """Шрифты"""
    font: pygame.font.Font = pygame.font.SysFont('arial', 20)
    small_font: pygame.font.Font = pygame.font.SysFont('arial', 16)
    title_font: pygame.font.Font = pygame.font.SysFont('arial', 36, bold=True)
    record_font: pygame.font.Font = pygame.font.SysFont('arial', 42, bold=True)

    def reset_game() -> None:
        """Сброс состояния игры"""
        nonlocal score, current_coins, food, milk, mice_killed, game_over, game_paused
        nonlocal spawn_timer, item_timer, mouse_timer, next_mouse_spawn

        for sprite in all_sprites:
            if sprite != cat:
                sprite.kill()

        score = 0.0
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

        cat.rect.center = (100, SCREEN_HEIGHT - 100)
        cat.velocity_y = 0.0
        cat.is_jumping = False
        cat.is_clouding = False
        cat.can_shoot = True
        cat.shoot_cooldown = 0
        cat.can_pass_high_obstacle = True

    def check_collision_with_obstacles(rect: pygame.Rect) -> bool:
        """Проверка столкновения с препятствиями"""
        for obstacle in obstacles:
            if rect.colliderect(obstacle.rect):
                return True
        return False

    """Главный игровой цикл"""
    running: bool = True
    while running:
        clock.tick(FPS)

        """Обновляем количество монет в меню"""
        game_menu.coins = total_coins + current_coins

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                update_high_score(score)
                update_money_score(total_coins + current_coins)
                save_game_state(game_menu, selected_accessory_type)
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if not game_over:
                        game_menu.active = not game_menu.active
                        if game_menu.active:
                            game_paused = True
                        else:
                            game_menu.show_instructions = False
                            game_menu.show_shop = False
                            game_menu.show_selection = False
                            game_paused = False
                            game_menu.save_shop_state(selected_accessory_type)

                if not game_menu.active:
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
                            yarn_ball: Optional[YarnBall] = cat.shoot()
                            if yarn_ball:
                                yarn_balls.add(yarn_ball)
                                all_sprites.add(yarn_ball)
                        elif event.key == pygame.K_b or event.key == ord('и'):
                            current_bg = (current_bg + 1) % len(backgrounds)
                    elif (event.key == pygame.K_r or event.key == ord('к')) and game_over:
                        reset_game()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos: Tuple[int, int] = pygame.mouse.get_pos()

                    if game_menu.active:
                        if game_menu.show_instructions:
                            game_menu.back_button.check_click(mouse_pos)
                        elif game_menu.show_shop:
                            for button in game_menu.shop_buttons:
                                clicked: bool = button.check_click(mouse_pos)
                                if clicked:
                                    """Если была покупка, обновляем счетчик монет"""
                                    if "Купить" in button.text:
                                        update_money_score(total_coins + current_coins)
                                    elif button.text == "Выбрать":
                                        game_menu.show_selection_menu()
                        elif game_menu.show_selection:
                            """Обработка выбора аксессуара"""
                            available_items: List[Tuple[str, int, str]] = [("Без аксессуара", 0, "none")]
                            if "hat" in game_menu.purchased_items:
                                available_items.append(("Шляпа", 1, "hat"))
                            if "glasses" in game_menu.purchased_items:
                                available_items.append(("Очки", 2, "glasses"))
                            if "bow" in game_menu.purchased_items:
                                available_items.append(("Бант", 3, "bow"))

                            if len(available_items) <= 1:
                                button_width: int = 200
                                button_height: int = 50
                                button_y: int = 200
                                shop_rect: pygame.Rect = pygame.Rect(
                                    SCREEN_WIDTH // 2 - button_width // 2,
                                    button_y,
                                    button_width,
                                    button_height
                                )
                                if shop_rect.collidepoint(mouse_pos):
                                    game_menu.back_to_shop()
                            else:
                                """Проверяем клик по карточкам"""
                                card_width: int = 150
                                card_height: int = 200
                                card_margin: int = 15
                                total_width: int = len(available_items) * card_width + (
                                            len(available_items) - 1) * card_margin
                                start_x: int = (SCREEN_WIDTH - total_width) // 2
                                y_pos: int = 180

                                for i, (name, accessory_id, item_id) in enumerate(available_items):
                                    card_x: int = start_x + i * (card_width + card_margin)
                                    button_rect: pygame.Rect = pygame.Rect(
                                        card_x + 20,
                                        y_pos + card_height - 40,
                                        card_width - 40,
                                        30
                                    )
                                    if button_rect.collidepoint(mouse_pos):
                                        selected_accessory_type = game_menu.select_accessory(accessory_id)
                                        cat.selected_accessory_type = selected_accessory_type
                                        cat.update_sprites()
                                        game_menu.save_shop_state(selected_accessory_type)

                                """Проверяем клик по кнопкам"""
                                button_width = 180
                                button_height = 45
                                button_spacing: int = 20
                                button_y = y_pos + card_height + 40
                                total_buttons_width: int = (button_width * 2) + button_spacing
                                buttons_start_x: int = (SCREEN_WIDTH - total_buttons_width) // 2

                                continue_rect: pygame.Rect = pygame.Rect(
                                    buttons_start_x,
                                    button_y,
                                    button_width,
                                    button_height
                                )
                                shop_rect = pygame.Rect(
                                    buttons_start_x + button_width + button_spacing,
                                    button_y,
                                    button_width,
                                    button_height
                                )

                                if continue_rect.collidepoint(mouse_pos):
                                    game_menu.continue_game()
                                elif shop_rect.collidepoint(mouse_pos):
                                    game_menu.back_to_shop()
                        else:
                            for button in game_menu.menu_buttons:
                                button.check_click(mouse_pos)

        """Обновление игры"""
        if not game_over and not game_paused and not game_menu.active:
            all_sprites.update()

            bg_x -= BACKGROUND_SPEED
            if bg_x <= -SCREEN_WIDTH:
                bg_x = 0

            """Спавн препятствий (с поддержкой группового спавна)"""
            spawn_timer += 1
            if spawn_timer >= 90:
                spawn_timer = 0

                """Получаем самое правое препятствие на экране"""
                last_obstacle: Optional[Obstacle] = None
                if obstacles:
                    last_obstacle = max(obstacles, key=lambda o: o.rect.right)

                """Решаем, создавать ли группу (15% шанс + проверка на безопасность)"""
                if random.random() < 0.15 and Obstacle.can_spawn_group(
                    last_obstacle.rect if last_obstacle else None
                ):
                    """При создании группы не используем облака"""
                    for i in range(2):
                        obstacle: Obstacle = Obstacle(pregrada_images, pregrada_types, is_group=True)

                        """Для препятствий в группе (кроме первого) немного смещаем позицию"""
                        if i > 0:
                            obstacle.rect.x += i * 245

                        obstacles.add(obstacle)
                        all_sprites.add(obstacle)
                else:
                    """Обычный одиночный спавн"""
                    obstacle = Obstacle(pregrada_images, pregrada_types)
                    obstacles.add(obstacle)
                    all_sprites.add(obstacle)

            """Спавн предметов"""
            item_timer += 1
            if item_timer >= 45:
                item_timer = 0
                item_type: str = random.choice(["coin", "fish", "meat", "milk"])

                max_attempts: int = 10
                for attempt in range(max_attempts):
                    item: Item = Item(item_type)

                    if not check_collision_with_obstacles(item.rect):
                        items.add(item)
                        all_sprites.add(item)
                        break
                    else:
                        item.kill()

            """Спавн мышек"""
            mouse_timer += 1
            if mouse_timer >= next_mouse_spawn:
                mouse_timer = 0
                next_mouse_spawn = random.randint(180, 480)

                mouse: Mouse = Mouse(cat.get_mouse_spawn_height())
                mice.add(mouse)
                all_sprites.add(mouse)

            """Проверка столкновений с препятствиями"""
            hits: List[Obstacle] = pygame.sprite.spritecollide(cat, obstacles, False)
            for hit in hits:
                if hit.type == "jump":
                    if not cat.is_jumping:
                        game_over = True
                        update_high_score(score)
                    elif cat.is_jumping and not cat.can_pass_high_obstacle:
                        game_over = True
                        update_high_score(score)

                elif hit.type == "low_jump" and not cat.is_jumping:
                    game_over = True
                    update_high_score(score)
                elif hit.type == "cloud" and not cat.is_clouding:
                    game_over = True
                    update_high_score(score)

            """Проверка столкновений с мышками"""
            mouse_hits: List[Mouse] = pygame.sprite.spritecollide(cat, mice, False)
            if mouse_hits:
                game_over = True
                update_high_score(score)

            """Проверка попадания клубков в мышек"""
            for yarn_ball in yarn_balls:
                mouse_hits = pygame.sprite.spritecollide(yarn_ball, mice, True)
                for mouse in mouse_hits:
                    yarn_ball.kill()
                    mice_killed += 1
                    score += 50
                    update_high_score(score)

            """Проверка сбора предметов"""
            collected: List[Item] = pygame.sprite.spritecollide(cat, items, True)
            for item in collected:
                if item.type == "coin":
                    current_coins += 1
                    score += 10
                    update_money_score(total_coins + current_coins)
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

            update_money_score(total_coins + current_coins)

        """Отрисовка фона"""
        screen.blit(backgrounds[current_bg], (bg_x, 0))
        screen.blit(backgrounds[current_bg], (bg_x + SCREEN_WIDTH, 0))

        """Нижняя дощечка"""
        pygame.draw.rect(screen, BROWN, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
        for i in range(0, SCREEN_WIDTH, 20):
            pygame.draw.line(screen, (110, 60, 30), (i, SCREEN_HEIGHT - 50), (i, SCREEN_HEIGHT), 1)

        all_sprites.draw(screen)

        """Определяем цвет текста"""
        text_color: Tuple[int, int, int]
        if current_bg == 1 or current_bg == 3:
            text_color = WHITE
        else:
            text_color = BLACK

        stats_x: int = SCREEN_WIDTH - 180
        stats_start_y: int = 20
        stats_spacing: int = 25

        """Отрисовка статистики"""
        draw_text(f"Рекорд: {int(high_score)}", text_color, stats_x, stats_start_y, font)
        draw_text(f"Монеты: {total_coins + current_coins}", text_color, stats_x, stats_start_y + stats_spacing, font)
        draw_text(f"Еда: {food}", text_color, stats_x, stats_start_y + stats_spacing * 2, font)
        draw_text(f"Молоко: {milk}", text_color, stats_x, stats_start_y + stats_spacing * 3, font)
        draw_text(f"Мыши: {mice_killed}", text_color, stats_x, stats_start_y + stats_spacing * 4, font)
        draw_text(f"Счет: {int(score)}", text_color, stats_x, stats_start_y + stats_spacing * 5, font)

        """Инструкции"""
        instructions_left_x: int = 15
        instructions_start_y: int = 20
        instructions_spacing: int = 22

        instructions: List[str] = [
            "Управление:",
            "ПРОБЕЛ - Высокий прыжок",
            "СТРЕЛКА ВВЕРХ - Низкий прыжок",
            "СТРЕЛКА ВНИЗ - Присесть",
            "СТРЕЛКА ВПРАВО - Выстрел",
            "B - Сменить фон",
            "P - Пауза",
            "R - Перезапуск"
        ]

        current_y: int = instructions_start_y
        for instruction in instructions:
            if instruction:
                draw_text(instruction, text_color, instructions_left_x, current_y, small_font)
            current_y += instructions_spacing

        """Экран паузы"""
        if game_paused and not game_over:
            overlay: pygame.Surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            draw_text("ПАУЗА", WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40, title_font, center_x=True,
                      center_y=True)
            draw_text("Нажми P для продолжения", WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10, small_font,
                      center_x=True, center_y=True)

        """Экран Game Over"""
        if game_over:
            overlay: pygame.Surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            center_x: int = SCREEN_WIDTH // 2
            game_over_start_y: int = 120

            if new_record_achieved:
                pygame.draw.rect(screen, GOLD, (center_x - 220, game_over_start_y - 20, 440, 70), 4, border_radius=12)
                pygame.draw.rect(screen, (30, 30, 30, 220), (center_x - 216, game_over_start_y - 16, 432, 62),
                                 border_radius=10)

                draw_text("НОВЫЙ РЕКОРД!", GOLD, center_x, game_over_start_y + 15, record_font, center_x=True,
                          center_y=True)
                game_over_start_y += 90
            else:
                game_over_start_y += 20

            draw_text("GAME OVER", RED, center_x, game_over_start_y, title_font, center_x=True, center_y=True)

            """Статистика Game Over"""
            stats_start_y: int = game_over_start_y + 60
            stat_spacing: int = 35

            stats_items: List[str] = [
                f"Финальный счет: {int(score)}",
                f"Собрано монет: {total_coins + current_coins}",
                f"Собрано еды: {food}",
                f"Собрано молока: {milk}",
                f"Убито мышек: {mice_killed}"
            ]

            for i, stat in enumerate(stats_items):
                draw_text(stat, WHITE, center_x, stats_start_y + i * stat_spacing, font, center_x=True, center_y=True)

            """Инструкция для перезапуска"""
            restart_y: int = stats_start_y + len(stats_items) * stat_spacing + 30
            draw_text("Нажми R для перезапуска", WHITE, center_x, restart_y, small_font, center_x=True, center_y=True)

        """Отрисовка меню"""
        game_menu.draw(screen, selected_accessory_type)
        pygame.display.flip()

    """Сохранение при выходе"""
    save_high_score(high_score)
    save_money_score(total_coins + current_coins)
    save_game_state(game_menu, selected_accessory_type)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()