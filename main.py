import pygame
from settings import WIDTH, HEIGHT, FPS, DECOR_COLOR
import planet_manager
from player import Player
from dialogue import DialogueBox
import boss_battle
import background
import vision

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
world_surface = pygame.Surface((WIDTH, HEIGHT))
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
transition_state = {
    "active": False,
    "phase": None,
    "alpha": 0,
    "target_room": None,
    "direction": None,
}


def request_room_change(new_room, direction):
    global transition_state
    if transition_state["active"]:
        return
    transition_state.update({
        "active": True,
        "phase": "out",
        "alpha": 0,
        "target_room": new_room,
        "direction": direction,
    })


def _complete_room_change():
    planet_manager.set_current_room(transition_state["target_room"])
    player.snap_to_edge(transition_state["direction"], WIDTH, HEIGHT)
    transition_state["phase"] = "in"


def start_boss_battle():
    boss_battle.start_boss_battle(
        dialogue_box,
        boss_key="guardian",
        on_complete=lambda: player.center_on_screen(WIDTH, HEIGHT),
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
                current_room_data = planet_manager.get_current_room_data()
                for npc in current_room_data["npcs"]:
                    if npc.is_near(player.pos):
                        lines, triggers_battle = npc.get_dialogue()
                        dialogue_box.start(
                            npc.name, lines,
                            on_complete=(lambda boss_key=npc.boss_key or "guardian": boss_battle.start_boss_battle(dialogue_box, boss_key=boss_key)) if triggers_battle else None,
                        )
                        break

    keys = pygame.key.get_pressed()

    room = planet_manager.get_current_room_data()
    if not dialogue_box.active and not transition_state["active"]:
        obstacles = list(room.get("obstacles", []))
        sky = room.get("sky")
        if sky:
            obstacles.append(pygame.Rect(0, 0, WIDTH, sky["height"]))

        player.handle_movement(
            keys,
            dt,
            WIDTH,
            HEIGHT,
            planet_manager.current_room,
            request_room_change,
            planet_manager.get_current_connections(),
            room.get("npcs", []),
            obstacles,
        )

    FADE_SPEED = 900
    if transition_state["active"]:
        if transition_state["phase"] == "out":
            transition_state["alpha"] += FADE_SPEED * dt
            if transition_state["alpha"] >= 255:
                transition_state["alpha"] = 255
                _complete_room_change()
        else:
            transition_state["alpha"] -= FADE_SPEED * dt
            if transition_state["alpha"] <= 0:
                transition_state["alpha"] = 0
                transition_state["active"] = False
                transition_state["phase"] = None
                transition_state["target_room"] = None
                transition_state["direction"] = None

    # --- draw ---, 
    room = planet_manager.get_current_room_data()
    if not background.draw_room_background(world_surface, room):
        world_surface.fill(room["color"])
        sky = room.get("sky")
        if sky:
            pygame.draw.rect(world_surface, sky["color"], pygame.Rect(0, 0, WIDTH, sky["height"]))

    for item in room.get("decor", []):
        background.draw(world_surface, item)

    for npc in room["npcs"]:
        npc.draw(world_surface)

    player.draw(world_surface)

    vision.apply_vision_zoom(screen, world_surface, player.pos, WIDTH, HEIGHT, coverage=0.7)

    dialogue_box.draw(screen)

    if transition_state["active"]:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(int(transition_state["alpha"]))
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

    pygame.display.flip()
    dt = clock.tick(FPS) / 1000

pygame.quit()