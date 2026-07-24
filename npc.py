import pygame
import gif_pygame
from PIL import Image
from settings import INTERACT_RANGE


def _load_gif_animation(path, size=None):
    image = Image.open(path)
    frames = []

    try:
        for frame_index in range(image.n_frames):
            image.seek(frame_index)
            rgba_frame = image.convert("RGBA")
            surface = pygame.image.frombuffer(rgba_frame.tobytes(), rgba_frame.size, "RGBA")
            if size is not None:
                surface = pygame.transform.smoothscale(surface, size)
            duration = image.info.get("duration", 1000) * 0.001
            frames.append([surface, duration])
    finally:
        image.close()

    return gif_pygame.GIFPygame(frames, -1)


class NPC:
    def __init__(self, x, y, name, color, lines, size=(40, 60), image_path=None, image_size=None):
        self.pos = pygame.Vector2(x, y)
        self.name = name
        self.color = color
        self.lines = lines  # list of strings shown one at a time
        self.image_path = image_path
        self.image_size = image_size
        self.image = None
        self.rect = pygame.Rect(x, y, *size)

    def _ensure_image(self):
        if self.image_path and self.image is None:
            try:
                if self.image_path.lower().endswith(".gif"):
                    self.image = _load_gif_animation(self.image_path, self.image_size)
                else:
                    self.image = pygame.image.load(self.image_path).convert_alpha()
                    if self.image_size is not None:
                        self.image = pygame.transform.smoothscale(self.image, self.image_size)
                self.rect = self.image.get_rect(topleft=(self.pos.x, self.pos.y))
            except Exception:
                try:
                    self.image = pygame.image.load(self.image_path).convert_alpha()
                    if self.image_size is not None:
                        self.image = pygame.transform.smoothscale(self.image, self.image_size)
                    self.rect = self.image.get_rect(topleft=(self.pos.x, self.pos.y))
                except Exception:
                    self.image = None

    def is_near(self, player_pos):
        return self.pos.distance_to(player_pos) <= INTERACT_RANGE

    def draw(self, screen):
        self._ensure_image()
        if self.image is not None:
            if hasattr(self.image, "render"):
                self.image.render(screen, self.rect.topleft)
            else:
                screen.blit(self.image, self.rect.topleft)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
