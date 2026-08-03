import math
import pygame

CHASER_SPEED = 140
CAPTURE_RADIUS = 32


class DarkFigure:
    """A shadowy, cloaked figure that hunts the player while active.

    It has no image asset - it's drawn directly with pygame primitives as a
    dark hooded silhouette with two glowing eyes, so it works immediately
    without needing new art. main.py is responsible for spawning it when the
    player enters a planet/room it should haunt, updating it each frame with
    the player's position, and checking has_captured() to trigger a capture.
    """

    def __init__(self, speed=CHASER_SPEED, capture_radius=CAPTURE_RADIUS):
        self.pos = pygame.Vector2(0, 0)
        self.speed = speed
        self.capture_radius = capture_radius
        self.active = False
        self.pause_timer = 0.0
        self._bob_timer = 0.0

    def spawn(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.active = True
        self.pause_timer = 0.0
        self._bob_timer = 0.0

    def spawn_with_delay(self, x, y, delay):
        """Like spawn(), but the figure stays put for `delay` seconds before
        resuming the chase - used when it follows the player into a new room
        so it doesn't unrealistically teleport straight onto them."""
        self.spawn(x, y)
        self.pause_timer = max(0.0, delay)

    def deactivate(self):
        self.active = False
        self.pause_timer = 0.0

    def update(self, dt, player_center):
        if not self.active:
            return

        if self.pause_timer > 0:
            self.pause_timer = max(0.0, self.pause_timer - dt)
            self._bob_timer += dt
            return

        direction = player_center - self.pos
        distance = direction.length()
        if distance > 1:
            direction.scale_to_length(min(self.speed * dt, distance))
            self.pos += direction

        self._bob_timer += dt

    def has_captured(self, player_center):
        if not self.active or self.pause_timer > 0:
            return False
        return self.pos.distance_to(player_center) <= self.capture_radius

    def get_rect(self):
        return pygame.Rect(int(self.pos.x - 20), int(self.pos.y - 44), 40, 60)

    def draw(self, screen):
        if not self.active or self.pause_timer > 0:
            return

        bob = math.sin(self._bob_timer * 4) * 4
        x = int(self.pos.x)
        y = int(self.pos.y + bob)

        body_color = (8, 8, 12)
        outline_color = (55, 15, 65)
        eye_color = (210, 30, 30)

        # soft dark aura
        aura = pygame.Surface((110, 140), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (5, 5, 15, 100), aura.get_rect())
        screen.blit(aura, (x - 55, y - 70))

        # hood
        head_radius = 15
        head_center = (x, y - 32)
        pygame.draw.circle(screen, body_color, head_center, head_radius)
        pygame.draw.circle(screen, outline_color, head_center, head_radius, width=2)

        # flowing, ragged cloak
        cloak_points = [
            (x - 4, y - 22),
            (x + 4, y - 22),
            (x + 27, y + 40),
            (x + 15, y + 33),
            (x + 7, y + 46),
            (x, y + 36),
            (x - 7, y + 46),
            (x - 15, y + 33),
            (x - 27, y + 40),
        ]
        pygame.draw.polygon(screen, body_color, cloak_points)
        pygame.draw.polygon(screen, outline_color, cloak_points, width=2)

        # glowing eyes, the only real color on the figure
        pygame.draw.circle(screen, eye_color, (x - 5, y - 34), 2)
        pygame.draw.circle(screen, eye_color, (x + 5, y - 34), 2)