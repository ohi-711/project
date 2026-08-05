# main menu after intro card
import pygame
from settings import WIDTH, HEIGHT, WHITE
import save_system

MENU_OPTIONS = ["Play", "Load Save File", "Settings", "Exit"]


class MainMenu:
    def __init__(self):
        self.cursor = 0
        self.state = "main"  # "main" | "settings" | "load_slots"
        self.title_font = pygame.font.SysFont(None, 64, bold=True)
        self.option_font = pygame.font.SysFont(None, 42)
        self.hint_font = pygame.font.SysFont(None, 24)
        self.slot_font = pygame.font.SysFont(None, 34)

        # load-slot sub-menu
        self.load_cursor = 0
        self.load_message = ""

    def reset(self):
        """Called whenever the menu is (re)entered"""
        self.cursor = 0
        self.state = "main"
        self.load_message = ""

    def handle_event(self, event):
        """Returns "play", "exit", or "load:<slot>" when the player has
        made that choice."""
        if event.type != pygame.KEYDOWN:
            return None

        if self.state == "settings":
            if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.state = "main"
            return None

        if self.state == "load_slots":
            return self._handle_load_slots_event(event)

        # state == "main" 
        if event.key == pygame.K_UP:
            self.cursor = (self.cursor - 1) % len(MENU_OPTIONS)
        elif event.key == pygame.K_DOWN:
            self.cursor = (self.cursor + 1) % len(MENU_OPTIONS)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
            selected = MENU_OPTIONS[self.cursor]
            if selected == "Play":
                return "play"
            elif selected == "Load Save File":
                self.state = "load_slots"
                self.load_cursor = 0
                self.load_message = ""
            elif selected == "Settings":
                self.state = "settings"
            elif selected == "Exit":
                return "exit"
        return None

    def _handle_load_slots_event(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
            self.state = "main"
            self.load_message = ""
        elif event.key == pygame.K_UP:
            self.load_cursor = (self.load_cursor - 1) % save_system.NUM_SLOTS
        elif event.key == pygame.K_DOWN:
            self.load_cursor = (self.load_cursor + 1) % save_system.NUM_SLOTS
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
            slot = self.load_cursor + 1
            if save_system.save_exists(slot):
                return f"load:{slot}"
            else:
                self.load_message = "That slot is empty."
        return None

    def draw(self, surface):
        surface.fill((10, 10, 20))
        if self.state == "settings":
            self._draw_settings(surface)
        elif self.state == "load_slots":
            self._draw_load_slots(surface)
        else:
            self._draw_main(surface)

    def _draw_main(self, surface):
        title_surf = self.title_font.render("Space Detective", True, WHITE)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 160))
        surface.blit(title_surf, title_rect)

        start_y = HEIGHT // 2 - 40
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

    def _draw_load_slots(self, surface):
        title_surf = self.title_font.render("Load Save File", True, WHITE)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 160))
        surface.blit(title_surf, title_rect)

        start_y = HEIGHT // 2 - 40
        spacing = 50
        for i in range(save_system.NUM_SLOTS):
            slot = i + 1
            summary = save_system.get_slot_summary(slot)
            label = f"Slot {slot}: " + (summary if summary else "Empty")
            color = (255, 230, 120) if i == self.load_cursor else WHITE
            marker = "> " if i == self.load_cursor else "  "
            surf = self.slot_font.render(marker + label, True, color)
            rect = surf.get_rect(center=(WIDTH // 2, start_y + i * spacing))
            surface.blit(surf, rect)

        if self.load_message:
            msg_surf = self.option_font.render(self.load_message, True, (220, 120, 120))
            msg_rect = msg_surf.get_rect(
                center=(WIDTH // 2, start_y + save_system.NUM_SLOTS * spacing + 30)
            )
            surface.blit(msg_surf, msg_rect)

        hint = self.hint_font.render(
            "[UP/DOWN] choose    [ENTER] load    [ESC] back", True, (160, 160, 160)
        )
        hint_rect = hint.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        surface.blit(hint, hint_rect)