import pygame
from typing import Tuple, Optional, Callable, Any
from constants import *

"""Класс кнопок"""
class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, action: Optional[Callable[[], Any]] = None) -> None:
        self.rect: pygame.Rect = pygame.Rect(x, y, width, height)
        self.text: str = text
        self.action: Optional[Callable[[], Any]] = action
        self.color: Tuple[int, int, int] = LIGHT_BLUE
        self.hover_color: Tuple[int, int, int] = (150, 200, 255)
        self.current_color: Tuple[int, int, int] = self.color
        self.font: pygame.font.Font = pygame.font.SysFont('arial', 20)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)

        text_surf: pygame.Surface = self.font.render(self.text, True, BLACK)
        text_rect: pygame.Rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos: Tuple[int, int]) -> bool:
        if self.rect.collidepoint(pos):
            self.current_color = self.hover_color
            return True
        else:
            self.current_color = self.color
            return False

    def check_click(self, pos: Tuple[int, int]) -> bool:
        if self.rect.collidepoint(pos):
            if self.action:
                self.action()
            return True
        return False


def draw_text(text: str, color: Tuple[int, int, int], x: int, y: int, font_obj: Optional[pygame.font.Font] = None,
              center_x: bool = False, center_y: bool = False) -> None:
    if font_obj is None:
        font_obj = pygame.font.SysFont('arial', 20)

    img: pygame.Surface = font_obj.render(text, True, color)
    rect: pygame.Rect = img.get_rect()

    if center_x:
        rect.centerx = x
    else:
        rect.x = x

    if center_y:
        rect.centery = y
    else:
        rect.y = y

    surface: pygame.Surface = pygame.display.get_surface()
    surface.blit(img, rect)


def get_text_color(current_bg: int) -> Tuple[int, int, int]:
    """Функция для определения цвета текста в зависимости от фона"""
    if current_bg == 1 or current_bg == 3:
        return WHITE
    else:
        return BLACK