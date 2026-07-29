import pygame
from settings import WIDTH, HEIGHT, DIALOGUE_BG, DIALOGUE_BORDER, WHITE, TEXT_SPEED


class DialogueBox:
    def __init__(self, chars_per_second=TEXT_SPEED):
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

        # for typewriter effect
        self.chars_per_second = chars_per_second
        self.wrapped_lines = [] # current line
        self.total_chars = 0 # total revealable chars in wrapped_lines
        self.revealed_chars = 0 # how many chars currently shown
        self.char_timer = 0.0
        self.line_complete = False

    def start(self, speaker, lines, on_complete=None):
        self.speaker = speaker
        self.lines = lines
        self.line_index = 0
        self.active = True
        self.on_complete = on_complete
        self._prepare_current_line()

    def update(self, dt):
        if not self.active or self.line_complete:
            return

        self.char_timer += dt
        target = int(self.char_timer * self.chars_per_second)
        if target > self.revealed_chars:
            self.revealed_chars = target
        if self.revealed_chars >= self.total_chars:
            self.revealed_chars = self.total_chars
            self.line_complete = True

    def advance(self):
        # When the player presses E, the whole line will be revealed
        if not self.line_complete:
            self.revealed_chars = self.total_chars
            self.line_complete = True
            return

        self.line_index += 1
        if self.line_index >= len(self.lines):
            self.active = False
            if self.on_complete:
                callback = self.on_complete
                self.on_complete = None
                callback()
        else:
            self._prepare_current_line()

    def _prepare_current_line(self):
        text = self.lines[self.line_index]
        padding = 20
        self.wrapped_lines = self._wrap_text(text, self.box_rect.width - padding * 2)

        self.total_chars = sum(len(line) for line in self.wrapped_lines) + max(len(self.wrapped_lines) - 1, 0)
        self.revealed_chars = 0
        self.char_timer = 0.0
        self.line_complete = self.total_chars == 0

    def _visible_wrapped_lines(self):
        remaining = self.revealed_chars
        visible = []
        for line in self.wrapped_lines:
            if remaining <= 0:
                break
            if remaining >= len(line):
                visible.append(line)
                remaining -= len(line) + 1  # +1 for the join char accounted for above
            else:
                visible.append(line[:remaining])
                remaining = 0
        return visible

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

        visible_lines = self._visible_wrapped_lines()
        for i, line in enumerate(visible_lines):
            surf = self.font.render(line, True, WHITE)
            screen.blit(surf, (self.box_rect.x + padding,
                                self.box_rect.y + 50 + i * 30))

        hint_text = "[E] continue" if self.line_complete else "[E] skip"
        hint = self.font.render(hint_text, True, (160, 160, 160))
        screen.blit(hint, (self.box_rect.right - hint.get_width() - padding,
                            self.box_rect.bottom - 35))