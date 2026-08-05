import pygame
from settings import WIDTH, HEIGHT, DIALOGUE_BG, DIALOGUE_BORDER, WHITE


class PauseMenu:

    OPTIONS = ["Resume", "Exit Game"]

    def __init__(self):
        self.active = False
        self.should_quit = False
        self.cursor = 0

        self.title_font = pygame.font.SysFont(None, 48, bold=True)
        self.option_font = pygame.font.SysFont(None, 38)
        self.hint_font = pygame.font.SysFont(None, 22)

        box_w, box_h = 380, 230
        self.box_rect = pygame.Rect(0, 0, box_w, box_h)
        self.box_rect.center = (WIDTH // 2, HEIGHT // 2)

    def open(self):
        self.active = True
        self.cursor = 0

    def close(self):
        self.active = False

    def toggle(self):
        if self.active:
            self.close()
        else:
            self.open()

    def handle_event(self, event):
        if not self.active or event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.close()
        elif event.key in (pygame.K_w, pygame.K_UP):
            self.cursor = (self.cursor - 1) % len(self.OPTIONS)
        elif event.key in (pygame.K_s, pygame.K_DOWN):
            self.cursor = (self.cursor + 1) % len(self.OPTIONS)
        elif event.key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE):
            self._select()

    def draw(self, screen):
        if not self.active:
            return

        # dim everything behind the menu
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, DIALOGUE_BG, self.box_rect, border_radius=12)
        pygame.draw.rect(screen, DIALOGUE_BORDER, self.box_rect, width=2, border_radius=12)

        title_surf = self.title_font.render("Paused", True, WHITE)
        title_rect = title_surf.get_rect(center=(self.box_rect.centerx, self.box_rect.y + 45))
        screen.blit(title_surf, title_rect)

        for i, option in enumerate(self.OPTIONS):
            color = (255, 230, 120) if i == self.cursor else WHITE
            marker = "> " if i == self.cursor else "  "
            surf = self.option_font.render(marker + option, True, color)
            rect = surf.get_rect(center=(self.box_rect.centerx, self.box_rect.y + 120 + i * 46))
            screen.blit(surf, rect)

        hint_surf = self.hint_font.render(
            "[W/S] choose   [E] select   [ESC] resume", True, (160, 160, 160)
        )
        hint_rect = hint_surf.get_rect(center=(self.box_rect.centerx, self.box_rect.bottom - 20))
        screen.blit(hint_surf, hint_rect)


# internal
    def _select(self):
        choice = self.OPTIONS[self.cursor]
        if choice == "Resume":
            self.close()
        elif choice == "Exit Game":
            self.should_quit = True