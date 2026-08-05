import pygame
from settings import WIDTH, HEIGHT, DIALOGUE_BG, DIALOGUE_BORDER, WHITE
import save_system


class PauseMenu:

    OPTIONS = ["Resume", "Save Game", "Exit Game"]

    def __init__(self):
        self.active = False
        self.should_quit = False
        self.cursor = 0
        self.state = "main"  # "main" | "save_slots"

        # save-slot sub-menu
        self.save_cursor = 0
        self.status_message = ""
        self._get_save_data = None  # set by main.py via set_save_data_provider

        self.title_font = pygame.font.SysFont(None, 48, bold=True)
        self.option_font = pygame.font.SysFont(None, 38)
        self.hint_font = pygame.font.SysFont(None, 22)
        self.slot_font = pygame.font.SysFont(None, 30)

        box_w, box_h = 380, 230
        self.box_rect = pygame.Rect(0, 0, box_w, box_h)
        self.box_rect.center = (WIDTH // 2, HEIGHT // 2)

        slot_box_w, slot_box_h = 460, 300
        self.slot_box_rect = pygame.Rect(0, 0, slot_box_w, slot_box_h)
        self.slot_box_rect.center = (WIDTH // 2, HEIGHT // 2)

    def set_save_data_provider(self, callback):
        """main.py returns a dict describing the current game state, so this menu can save it"""
        self._get_save_data = callback

    def open(self):
        self.active = True
        self.cursor = 0
        self.state = "main"
        self.status_message = ""

    def close(self):
        self.active = False
        self.state = "main"
        self.status_message = ""

    def toggle(self):
        if self.active:
            self.close()
        else:
            self.open()

    def handle_event(self, event):
        if not self.active or event.type != pygame.KEYDOWN:
            return

        if self.state == "save_slots":
            self._handle_save_slots_event(event)
            return

        # state == "main"
        if event.key == pygame.K_ESCAPE:
            self.close()
        elif event.key in (pygame.K_w, pygame.K_UP):
            self.cursor = (self.cursor - 1) % len(self.OPTIONS)
        elif event.key in (pygame.K_s, pygame.K_DOWN):
            self.cursor = (self.cursor + 1) % len(self.OPTIONS)
        elif event.key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE):
            self._select()

    def _handle_save_slots_event(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
            self.state = "main"
            self.status_message = ""
        elif event.key in (pygame.K_w, pygame.K_UP):
            self.save_cursor = (self.save_cursor - 1) % save_system.NUM_SLOTS
        elif event.key in (pygame.K_s, pygame.K_DOWN):
            self.save_cursor = (self.save_cursor + 1) % save_system.NUM_SLOTS
        elif event.key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE):
            slot = self.save_cursor + 1
            data = self._get_save_data() if self._get_save_data else None
            if data is not None and save_system.save_game(slot, data):
                self.status_message = f"Saved to Slot {slot}!"
            else:
                self.status_message = "Couldn't save right now."

    def draw(self, screen):
        if not self.active:
            return

        # dim everything behind the menu
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        if self.state == "save_slots":
            self._draw_save_slots(screen)
        else:
            self._draw_main(screen)

    def _draw_main(self, screen):
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

    def _draw_save_slots(self, screen):
        pygame.draw.rect(screen, DIALOGUE_BG, self.slot_box_rect, border_radius=12)
        pygame.draw.rect(screen, DIALOGUE_BORDER, self.slot_box_rect, width=2, border_radius=12)

        title_surf = self.title_font.render("Save Game", True, WHITE)
        title_rect = title_surf.get_rect(center=(self.slot_box_rect.centerx, self.slot_box_rect.y + 40))
        screen.blit(title_surf, title_rect)

        start_y = self.slot_box_rect.y + 100
        spacing = 40
        for i in range(save_system.NUM_SLOTS):
            slot = i + 1
            summary = save_system.get_slot_summary(slot)
            label = f"Slot {slot}: " + (summary if summary else "Empty")
            color = (255, 230, 120) if i == self.save_cursor else WHITE
            marker = "> " if i == self.save_cursor else "  "
            surf = self.slot_font.render(marker + label, True, color)
            rect = surf.get_rect(center=(self.slot_box_rect.centerx, start_y + i * spacing))
            screen.blit(surf, rect)

        if self.status_message:
            msg_surf = self.slot_font.render(self.status_message, True, (140, 220, 140))
            msg_rect = msg_surf.get_rect(
                center=(self.slot_box_rect.centerx, start_y + save_system.NUM_SLOTS * spacing + 20)
            )
            screen.blit(msg_surf, msg_rect)

        hint_surf = self.hint_font.render(
            "[W/S] choose   [E] save   [ESC] back", True, (160, 160, 160)
        )
        hint_rect = hint_surf.get_rect(center=(self.slot_box_rect.centerx, self.slot_box_rect.bottom - 20))
        screen.blit(hint_surf, hint_rect)

    # internal
    def _select(self):
        choice = self.OPTIONS[self.cursor]
        if choice == "Resume":
            self.close()
        elif choice == "Save Game":
            self.state = "save_slots"
            self.save_cursor = 0
            self.status_message = ""
        elif choice == "Exit Game":
            self.should_quit = True