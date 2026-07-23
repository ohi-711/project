import pygame
from settings import INTERACT_RANGE


class NPC:
    def __init__(self, x, y, name, color, lines, size=(40, 60)):
        self.pos = pygame.Vector2(x, y)
        self.name = name
        self.color = color
        self.lines = lines  # list of strings shown one at a time
        self.rect = pygame.Rect(x, y, *size)

    def is_near(self, player_pos):
        return self.pos.distance_to(player_pos) <= INTERACT_RANGE

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        font = pygame.font.SysFont(None, 22)
        label = font.render(self.name, True, (255, 255, 255))
        screen.blit(label, (self.rect.x, self.rect.y - 22))