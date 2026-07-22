import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Room Transition Demo")
clock = pygame.time.Clock()
running = True
dt = 0
player_speed = 300

char_front = pygame.image.load("assets/character-front.png").convert_alpha()
char_back = pygame.image.load("assets/character-back.png").convert_alpha()
char_left = pygame.image.load("assets/character-left.png").convert_alpha()
char_right = pygame.image.load("assets/character-right.png").convert_alpha()
character = char_front

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

rooms = {
    "room1": {
        "color": (140, 90, 180),
        "name": "Starting Room",
        "decor": [(180, 140, 100, 100), (900, 180, 120, 120)],
    },
    "room2": {
        "color": (90, 140, 200),
        "name": "Sky Room",
        "decor": [(240, 320, 140, 90), (940, 120, 80, 180)],
    },
    "room3": {
        "color": (70, 110, 80),
        "name": "Cave Room",
        "decor": [(420, 240, 110, 110), (860, 430, 140, 90)],
    },
}

room_connections = {
    "room1": {"left": None, "right": "room2", "up": None, "down": None},
    "room2": {"left": "room1", "right": None, "up": None, "down": "room3"},
    "room3": {"left": None, "right": None, "up": "room2", "down": None},
}

current_room = "room1"


def change_room(direction):
    global current_room, player_pos

    next_room = room_connections[current_room][direction]
    if next_room is None:
        return

    current_room = next_room

    if direction == "left":
        player_pos.x = screen.get_width() - 40
    elif direction == "right":
        player_pos.x = 40
    elif direction == "up":
        player_pos.y = screen.get_height() - 40
    elif direction == "down":
        player_pos.y = 40


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        character = char_back
        player_pos.y -= player_speed * dt
        if player_pos.y < 0:
            change_room("up")
    if keys[pygame.K_s]:
        character = char_front
        player_pos.y += player_speed * dt
        if player_pos.y > screen.get_height():
            change_room("down")
    if keys[pygame.K_a]:
        character = char_left
        player_pos.x -= player_speed * dt
        if player_pos.x < 0:
            change_room("left")
    if keys[pygame.K_d]:
        character = char_right
        player_pos.x += player_speed * dt
        if player_pos.x > screen.get_width():
            change_room("right")

    # fill the screen with the current room's color
    screen.fill(rooms[current_room]["color"])

    for x, y, w, h in rooms[current_room]["decor"]:
        pygame.draw.rect(screen, (40, 40, 40), pygame.Rect(x, y, w, h))

    font = pygame.font.SysFont(None, 36)
    room_label = font.render(rooms[current_room]["name"], True, "white")
    screen.blit(room_label, (20, 20))

    screen.blit(character, player_pos)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()