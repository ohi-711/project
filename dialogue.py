import pygame
from settings import WIDTH, HEIGHT, DIALOGUE_BG, DIALOGUE_BORDER, WHITE


class DialogueBox:
    """Owns its own state: whether it's open, which lines it's showing,
    and which line index we're on. main.py just asks it to draw/advance."""

    def __init__(self):
        self.active = False
        self.speaker = ""
        self.lines = []
        self.line_index = 0
        self.on_complete = None
        self.font = pygame.font.SysFont(None, 32)
        self.name_font = pygame.font.SysFont(None, 28, bold=True)

        # box geometry: bottom section of the screen
        self.box_height = 180
        self.box_rect = pygame.Rect(40, HEIGHT - self.box_height - 30,
                                     WIDTH - 80, self.box_height)

    def start(self, speaker, lines, on_complete=None):
        self.speaker = speaker
        self.lines = lines
        self.line_index = 0
        self.active = True
        self.on_complete = on_complete

    def advance(self):
        """Call this when the player presses the 'continue' key."""
        self.line_index += 1
        if self.line_index >= len(self.lines):
            self.active = False
            if self.on_complete:
                callback = self.on_complete
                self.on_complete = None
                callback()

    def _wrap_text(self, text, max_width):
        words = text.split(" ")
        lines, current = [], ""
        for word in words:
            test = f"{current} {word}".strip()
            if self.font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def draw(self, screen):
        if not self.active:
            return

        pygame.draw.rect(screen, DIALOGUE_BG, self.box_rect, border_radius=10)
        pygame.draw.rect(screen, DIALOGUE_BORDER, self.box_rect, width=2, border_radius=10)

        padding = 20
        name_surf = self.name_font.render(self.speaker, True, WHITE)
        screen.blit(name_surf, (self.box_rect.x + padding, self.box_rect.y + 12))

        text = self.lines[self.line_index]
        wrapped = self._wrap_text(text, self.box_rect.width - padding * 2)
        for i, line in enumerate(wrapped):
            surf = self.font.render(line, True, WHITE)
            screen.blit(surf, (self.box_rect.x + padding,
                                self.box_rect.y + 50 + i * 30))

        hint = self.font.render("[E] continue", True, (160, 160, 160))
        screen.blit(hint, (self.box_rect.right - hint.get_width() - padding,
                            self.box_rect.bottom - 35))