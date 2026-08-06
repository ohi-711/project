"""

"""

import math
import pygame
from settings import WIDTH, HEIGHT, WHITE, DIALOGUE_BG, DIALOGUE_BORDER, INTERACT_RANGE
from game_state import game_state

# used by game_state.transports to mark the network as unlocked
TRANSPORT_UNLOCK_ID = "stargate"

PLANET_DESTINATIONS = {
    "home": "Home World",
    "nova": "Nova Prime",
}

BOX_SIZE = (40, 40)
LOCKED_COLOR = (90, 30, 30)
LOCKED_OUTLINE = (140, 60, 60)
UNLOCKED_COLOR = (200, 30, 30)
UNLOCKED_OUTLINE = (255, 140, 140)

LOCKED_MESSAGE = [
    "The pad is dark and unresponsive.",
    "Something needs to happen before it will activate.",
]


def is_unlocked():
    return game_state.has_transport(TRANSPORT_UNLOCK_ID)


def get_box_rect(box_data):
    size = box_data.get("size", BOX_SIZE)
    return pygame.Rect(box_data["x"], box_data["y"], *size)


def is_near(box_data, player_pos):
    rect = get_box_rect(box_data)
    return pygame.Vector2(rect.center).distance_to(player_pos) <= INTERACT_RANGE


def draw(screen, box_data):
    rect = get_box_rect(box_data)
    unlocked = is_unlocked()

    if unlocked:
        # gentle pulsing glow so an active pad reads as "on" at a glance
        t = pygame.time.get_ticks() / 1000
        pulse = int(6 + 4 * math.sin(t * 3))
        glow = pygame.Surface((rect.width + pulse * 2, rect.height + pulse * 2), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*UNLOCKED_COLOR, 70), glow.get_rect(), border_radius=8)
        screen.blit(glow, (rect.x - pulse, rect.y - pulse))
        fill, outline = UNLOCKED_COLOR, UNLOCKED_OUTLINE
    else:
        fill, outline = LOCKED_COLOR, LOCKED_OUTLINE

    pygame.draw.rect(screen, fill, rect, border_radius=4)
    pygame.draw.rect(screen, outline, rect, width=2, border_radius=4)


class TransportMenu:
    """Destination-picker shown after interacting with an unlocked
    TransportBox. Owned/drawn/handled by main.py the same way as
    dialogue_box and courtroom_battle_ui."""

    def __init__(self):
        self.active = False
        self.cursor = 0
        self.destinations = []
        self.on_select = None

        self.font = pygame.font.SysFont(None, 30)
        self.title_font = pygame.font.SysFont(None, 28, bold=True)
        self.hint_font = pygame.font.SysFont(None, 22)

        box_w, box_h = 360, 260
        self.box_rect = pygame.Rect(0, 0, box_w, box_h)
        self.box_rect.center = (WIDTH // 2, HEIGHT // 2)

    def open(self, current_planet, on_select):
        """current_planet is excluded from the list - no point offering a
        trip to where you already are. on_select(destination_key) is
        called once the player confirms a choice."""
        self.destinations = [key for key in PLANET_DESTINATIONS if key != current_planet]
        self.cursor = 0
        self.on_select = on_select
        self.active = True

    def close(self):
        self.active = False
        self.on_select = None

    def handle_event(self, event):
        if not self.active or event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.close()
            return

        if not self.destinations:
            return

        if event.key == pygame.K_UP:
            self.cursor = (self.cursor - 1) % len(self.destinations)
        elif event.key == pygame.K_DOWN:
            self.cursor = (self.cursor + 1) % len(self.destinations)
        elif event.key == pygame.K_e:
            destination = self.destinations[self.cursor]
            callback = self.on_select
            self.close()
            if callback:
                callback(destination)

    def draw(self, screen):
        if not self.active:
            return

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, DIALOGUE_BG, self.box_rect, border_radius=10)
        pygame.draw.rect(screen, DIALOGUE_BORDER, self.box_rect, width=2, border_radius=10)

        title_surf = self.title_font.render("Travel to...", True, WHITE)
        title_rect = title_surf.get_rect(center=(self.box_rect.centerx, self.box_rect.y + 32))
        screen.blit(title_surf, title_rect)

        if not self.destinations:
            msg = self.font.render("(no other destinations yet)", True, (180, 180, 180))
            msg_rect = msg.get_rect(center=self.box_rect.center)
            screen.blit(msg, msg_rect)
        else:
            start_y = self.box_rect.y + 90
            spacing = 40
            for i, key in enumerate(self.destinations):
                label = PLANET_DESTINATIONS.get(key, key)
                color = (255, 230, 120) if i == self.cursor else WHITE
                marker = "> " if i == self.cursor else "  "
                surf = self.font.render(marker + label, True, color)
                rect = surf.get_rect(center=(self.box_rect.centerx, start_y + i * spacing))
                screen.blit(surf, rect)

        hint_surf = self.hint_font.render(
            "[UP/DOWN] choose   [E] travel   [ESC] cancel", True, (160, 160, 160)
        )
        hint_rect = hint_surf.get_rect(center=(self.box_rect.centerx, self.box_rect.bottom - 20))
        screen.blit(hint_surf, hint_rect)