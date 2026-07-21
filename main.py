import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

char_front = pygame.image.load("assets/character-front.png").convert_alpha()
char_back = pygame.image.load("assets/character-back.png").convert_alpha()
char_left = pygame.image.load("assets/character-left.png").convert_alpha()
char_right = pygame.image.load("assets/character-right.png").convert_alpha()
character = char_front

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        character = char_back
        player_pos.y -= 300 * dt
    if keys[pygame.K_s]:
        character = char_front
        player_pos.y += 300 * dt
    if keys[pygame.K_a]:
        character = char_left
        player_pos.x -= 300 * dt
    if keys[pygame.K_d]:
        character = char_right
        player_pos.x += 300 * dt

    screen.blit(character, player_pos)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()