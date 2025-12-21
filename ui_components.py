import pygame
from constants import *


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


def draw_text(text, color, x, y, font_obj=None, center_x=False, center_y=False):
    if font_obj is None:
        font_obj = pygame.font.SysFont('arial', 20)

    img = font_obj.render(text, True, color)
    rect = img.get_rect()

    if center_x:
        rect.centerx = x
    else:
        rect.x = x

    if center_y:
        rect.centery = y
    else:
        rect.y = y

    # Получаем активную поверхность
    surface = pygame.display.get_surface()
    surface.blit(img, rect)


def get_text_color(current_bg):
    """Функция для определения цвета текста в зависимости от фона"""
    if current_bg == 1 or current_bg == 3:
        return WHITE
    else:
        return BLACK