import pygame
import gif_pygame
from PIL import Image
from settings import INTERACT_RANGE
from game_state import game_state


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
    def __init__(self, x, y, name, color, lines, size=(40, 60), image_path=None, image_size=None,
                 clue_id=None, repeat_lines=None,
                 required_clues=None, on_all_clues_lines=None, boss_key=None):
        self.pos = pygame.Vector2(x, y)
        self.name = name
        self.color = color
        self.lines = lines  # list of strings shown one at a time
        self.image_path = image_path
        self.image_size = image_size
        self.image = None
        self.rect = pygame.Rect(x, y, *size)

        # --- clue / boss-gate behavior ---
        self.clue_id = clue_id                      # clue this NPC gives out, if any
        self.repeat_lines = repeat_lines or lines    # shown on repeat visits after clue given
        self.required_clues = required_clues         # list of clue_ids needed to trigger the boss
        self.on_all_clues_lines = on_all_clues_lines  # lines shown once all clues are gathered
        self.boss_key = boss_key

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

    def get_dialogue(self):
        # Returns (lines, triggers_battle) for the current interaction.
        if self.required_clues is not None:
            if game_state.has_all(self.required_clues):
                return self.on_all_clues_lines or self.lines, True
            return self.lines, False

        if self.clue_id is not None:
            if not game_state.has(self.clue_id):
                game_state.collect(self.clue_id)
                return self.lines, False
            return self.repeat_lines, False

        return self.lines, False

    def draw(self, screen):
        self._ensure_image()
        if self.image is not None:
            if hasattr(self.image, "render"):
                self.image.render(screen, self.rect.topleft)
            else:
                screen.blit(self.image, self.rect.topleft)
        else:
            pygame.draw.rect(screen, self.color, self.rect)