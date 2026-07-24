import pygame
from settings import WIDTH, HEIGHT, FPS, DECOR_COLOR
from rooms import rooms
from player import Player
from dialogue import DialogueBox
import background

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Room Transition Demo")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
background.load_decor_sprites()

# --- load sprites -----------------------------------------------------
sprites = {
    "front": pygame.image.load("assets/sprites/character-front.png").convert_alpha(),
    "back": pygame.image.load("assets/sprites/character-back.png").convert_alpha(),
    "left": pygame.image.load("assets/sprites/character-left.png").convert_alpha(),
    "right": pygame.image.load("assets/sprites/character-right.png").convert_alpha(),
}

player = Player(WIDTH / 2, HEIGHT / 2, sprites)
dialogue_box = DialogueBox()
current_room = "room1"

def change_room(new_room):
    global current_room
    current_room = new_room


def start_boss_battle():
    """Placeholder for the real boss battle -- for now, just shows some
    filler dialogue so the flow can be tested end-to-end. Swap this out
    later for whatever battle system you build."""
    dialogue_box.start(
        "???",
        [
            "The ground shakes as a shadow rises before you...",
            "(Boss battle would start here!)",
            "You strike true. The Guardian falls.",
            "You have proven yourself worthy.",
        ],
    )


running = True
dt = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            if dialogue_box.active:
                dialogue_box.advance()
            else:
                # look for a nearby NPC to start talking to
                for npc in rooms[current_room]["npcs"]:
                    if npc.is_near(player.pos):
                        lines, triggers_battle = npc.get_dialogue()
                        dialogue_box.start(
                            npc.name, lines,
                            on_complete=start_boss_battle if triggers_battle else None,
                        )
                        break

    keys = pygame.key.get_pressed()

    # freeze movement while a conversation is open
    if not dialogue_box.active:
        player.handle_movement(keys, dt, WIDTH, HEIGHT, current_room, change_room, rooms[current_room].get("npcs", []))

    # --- draw ---
    room = rooms[current_room]
    screen.fill(room["color"])

    for item in room.get("decor", []):
        background.draw(screen, item)

    for npc in room["npcs"]:
        npc.draw(screen)

    player.draw(screen)
    dialogue_box.draw(screen)

    pygame.display.flip()
    dt = clock.tick(FPS) / 1000

pygame.quit()