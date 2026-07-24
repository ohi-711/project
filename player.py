import pygame
from settings import PLAYER_SPEED
from rooms import room_connections


class Player:
    def __init__(self, x, y, sprites):
        # sprites: {"front": img, "back": img, "left": img, "right": img}
        self.pos = pygame.Vector2(x, y)
        self.sprites = sprites
        self.facing = "front"

    @property
    def image(self):
        return self.sprites[self.facing]

    def handle_movement(self, keys, dt, screen_w, screen_h, current_room, on_room_change, npcs=None):
        """Moves the player and triggers on_room_change(direction) if they
        walk off an edge that has a connected room."""
        # compute movement delta
        dx = dy = 0
        if keys[pygame.K_w]:
            self.facing = "back"
            dy -= PLAYER_SPEED * dt
        if keys[pygame.K_s]:
            self.facing = "front"
            dy += PLAYER_SPEED * dt
        if keys[pygame.K_a]:
            self.facing = "left"
            dx -= PLAYER_SPEED * dt
        if keys[pygame.K_d]:
            self.facing = "right"
            dx += PLAYER_SPEED * dt

        # get player size from current image
        player_size = self.image.get_rect().size

        # apply horizontal movement and check NPC collisions using swept rect
        if dx != 0:
            new_x = self.pos.x + dx
            left = min(self.pos.x, new_x)
            width = abs(new_x - self.pos.x) + player_size[0]
            swept = pygame.Rect(left, self.pos.y, width, player_size[1])
            blocked = False
            if npcs:
                for npc in npcs:
                    if hasattr(npc, "rect") and swept.colliderect(npc.rect):
                        blocked = True
                        break
            if not blocked:
                self.pos.x = new_x

        # apply vertical movement and check NPC collisions using swept rect
        if dy != 0:
            new_y = self.pos.y + dy
            top = min(self.pos.y, new_y)
            height = abs(new_y - self.pos.y) + player_size[1]
            swept = pygame.Rect(self.pos.x, top, player_size[0], height)
            blocked = False
            if npcs:
                for npc in npcs:
                    if hasattr(npc, "rect") and swept.colliderect(npc.rect):
                        blocked = True
                        break
            if not blocked:
                self.pos.y = new_y

        # check room transitions after movement
        if self.pos.y < 0:
            self._try_change_room(current_room, "up", screen_w, screen_h, on_room_change)
        if self.pos.y > screen_h:
            self._try_change_room(current_room, "down", screen_w, screen_h, on_room_change)
        if self.pos.x < 0:
            self._try_change_room(current_room, "left", screen_w, screen_h, on_room_change)
        if self.pos.x > screen_w:
            self._try_change_room(current_room, "right", screen_w, screen_h, on_room_change)

    def _try_change_room(self, current_room, direction, screen_w, screen_h, on_room_change):
        next_room = room_connections[current_room][direction]
        if next_room is None:
            return
        # snap the player to the opposite edge of the new room
        if direction == "left":
            self.pos.x = screen_w - 40
        elif direction == "right":
            self.pos.x = 40
        elif direction == "up":
            self.pos.y = screen_h - 40
        elif direction == "down":
            self.pos.y = 40
        on_room_change(next_room)

    def draw(self, screen):
        screen.blit(self.image, self.pos)