import pygame
from settings import PLAYER_SPEED


class Player:
    def __init__(self, x, y, sprites):
        # sprites: {"front": img, "back": img, "left": img, "right": img}
        self.pos = pygame.Vector2(x, y)
        self.sprites = sprites
        self.facing = "front"

    @property
    def image(self):
        return self.sprites[self.facing]

    def handle_movement(self, keys, dt, screen_w, screen_h, current_room, on_room_change, room_connections, npcs=None, obstacles=None, mask_obstacles=None):
        """Moves the player and runs on_room_change(direction) if they
        walk off an edge that has a connected room."""

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

        player_size = self.image.get_rect().size

        # horizontal movement
        if dx != 0:
            new_x = self.pos.x + dx
            left = min(self.pos.x, new_x)
            width = abs(new_x - self.pos.x) + player_size[0]
            swept = pygame.Rect(left, self.pos.y, width, player_size[1])
            blocked = False
            if obstacles:
                for obstacle in obstacles:
                    if swept.colliderect(obstacle):
                        blocked = True
                        break
            if not blocked:
                test_rect = pygame.Rect(new_x, self.pos.y, *player_size)
                if self._hits_mask_obstacles(test_rect, mask_obstacles):
                    blocked = True
            if not blocked:
                self.pos.x = new_x

        # vertical movement
        if dy != 0:
            new_y = self.pos.y + dy
            top = min(self.pos.y, new_y)
            height = abs(new_y - self.pos.y) + player_size[1]
            swept = pygame.Rect(self.pos.x, top, player_size[0], height)
            blocked = False
            if obstacles:
                for obstacle in obstacles:
                    if swept.colliderect(obstacle):
                        blocked = True
                        break
            if not blocked:
                test_rect = pygame.Rect(self.pos.x, new_y, *player_size)
                if self._hits_mask_obstacles(test_rect, mask_obstacles):
                    blocked = True
            if not blocked:
                self.pos.y = new_y

        # check room transitions after movement
        if self.pos.y < 0:
            self._try_change_room(current_room, "up", screen_w, screen_h, on_room_change, room_connections)
        if self.pos.y + player_size[1] > screen_h:
            self._try_change_room(current_room, "down", screen_w, screen_h, on_room_change, room_connections)
        if self.pos.x < 0:
            self._try_change_room(current_room, "left", screen_w, screen_h, on_room_change, room_connections)
        if self.pos.x + player_size[0] > screen_w:
            self._try_change_room(current_room, "right", screen_w, screen_h, on_room_change, room_connections)
            
    # for letting the player go through transparent parts of the decor.
    def _hits_mask_obstacles(self, rect, mask_obstacles):
        if not mask_obstacles:
            return False
        player_mask = pygame.Mask(rect.size, fill=True)
        for mask, obs_rect in mask_obstacles:
            if not rect.colliderect(obs_rect):
                continue
            offset = (obs_rect.x - rect.x, obs_rect.y - rect.y)
            if player_mask.overlap(mask, offset):
                return True
        return False

    def _try_change_room(self, current_room, direction, screen_w, screen_h, on_room_change, room_connections):
        next_room = room_connections[current_room][direction]
        if next_room is None:
            player_size = self.image.get_rect().size
            if direction == "left":
                self.pos.x = max(self.pos.x, 0)
            elif direction == "right":
                self.pos.x = min(self.pos.x, screen_w - player_size[0])
            elif direction == "up":
                self.pos.y = max(self.pos.y, 0)
            elif direction == "down":
                self.pos.y = min(self.pos.y, screen_h - player_size[1])
            return
        on_room_change(next_room, direction)

    def snap_to_edge(self, direction, screen_w, screen_h):
        if direction == "left":
            self.pos.x = screen_w - 40
        elif direction == "right":
            self.pos.x = 40
        elif direction == "up":
            self.pos.y = screen_h - 40
        elif direction == "down":
            self.pos.y = 40

    def center_on_screen(self, screen_w, screen_h):
        self.pos = pygame.Vector2(screen_w / 2, screen_h / 2)

    def draw(self, screen):
        screen.blit(self.image, self.pos)
