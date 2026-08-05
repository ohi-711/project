# main menu after intro card
import pygame
from settings import WIDTH, HEIGHT, WHITE

MENU_OPTIONS = ["Play", "Settings", "Exit"]


class MainMenu:
    def __init__(self):
        self.cursor = 0
        self.state = "main"  # "main" | "settings"
        self.title_font = pygame.font.SysFont(None, 64, bold=True)
        self.option_font = pygame.font.SysFont(None, 42)
        self.hint_font = pygame.font.SysFont(None, 24)

    def reset(self):
        """Called whenever the menu is (re)entered"""
        self.cursor = 0
        self.state = "main"

    def handle_event(self, event):
        """Returns "play" or "exit" when the player has made that choice"""
        if event.type != pygame.KEYDOWN:
            return None

        if self.state == "settings":
            if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.state = "main"
            return None

        # state == "main"
        if event.key == pygame.K_UP:
            self.cursor = (self.cursor - 1) % len(MENU_OPTIONS)
        elif event.key == pygame.K_DOWN:
            self.cursor = (self.cursor + 1) % len(MENU_OPTIONS)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
            selected = MENU_OPTIONS[self.cursor]
            if selected == "Play":
                return "play"
            elif selected == "Settings":
                self.state = "settings"
            elif selected == "Exit":
                return "exit"
        return None

    def draw(self, surface):
        surface.fill((10, 10, 20))
        if self.state == "settings":
            self._draw_settings(surface)
        else:
            self._draw_main(surface)

    def _draw_main(self, surface):
        title_surf = self.title_font.render("Space Detective", True, WHITE)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 140))
        surface.blit(title_surf, title_rect)

        start_y = HEIGHT // 2 - 20
        spacing = 56
        for i, option in enumerate(MENU_OPTIONS):
            color = (255, 230, 120) if i == self.cursor else WHITE
            label = ("> " if i == self.cursor else "  ") + option
            surf = self.option_font.render(label, True, color)
            rect = surf.get_rect(center=(WIDTH // 2, start_y + i * spacing))
            surface.blit(surf, rect)

        hint = self.hint_font.render("[UP/DOWN] choose    [ENTER] select", True, (160, 160, 160))
        hint_rect = hint.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        surface.blit(hint, hint_rect)

    def _draw_settings(self, surface):
        title_surf = self.title_font.render("Settings", True, WHITE)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        surface.blit(title_surf, title_rect)

        # placeholder - nothing configurable yet
        placeholder = self.option_font.render("(Nothing here yet)", True, (160, 160, 160))
        placeholder_rect = placeholder.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        surface.blit(placeholder, placeholder_rect)

        hint = self.hint_font.render("[ESC] back", True, (160, 160, 160))
        hint_rect = hint.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        surface.blit(hint, hint_rect)