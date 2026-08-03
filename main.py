import pygame
from settings import WIDTH, HEIGHT, FPS, DECOR_COLOR, TEXT_SPEED
import planet_manager
from player import Player
from dialogue import DialogueBox
import boss_battle
import courtroom_battle
from transport import start_transport_segment
import background
import vision
from resource_path import resource_path

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
world_surface = pygame.Surface((WIDTH, HEIGHT))
pygame.display.set_caption("Room Transition Demo")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
background.load_decor_sprites()

# intro
thumbnail_image = pygame.image.load(resource_path("assets/intro/thumbnail.png")).convert_alpha()
intro_state = "thumbnail"
intro_timer = 0.0
thumbnail_duration = 1.8
instructions_duration = 4.0
transition_duration = 1.0
intro_transition_alpha = 0
intro_font = pygame.font.SysFont(None, 34)

# typewriter effect for the intro text
INSTRUCTION_LINES = [
    "You are a space detective travelling across planets to solve problems.",
    "",
    "Use WASD to move around and E to talk to people.",
    "",
    "Press Enter or Space to begin.",
]
INSTRUCTION_TOTAL_CHARS = sum(len(line) for line in INSTRUCTION_LINES if line)
INSTRUCTION_CHARS_PER_SECOND = TEXT_SPEED
instructions_skip_typing = False


def _revealed_instruction_lines():
    if instructions_skip_typing:
        revealed_total = INSTRUCTION_TOTAL_CHARS
    else:
        revealed_total = min(INSTRUCTION_TOTAL_CHARS, int(intro_timer * INSTRUCTION_CHARS_PER_SECOND))

    lines = []
    remaining = revealed_total
    for line in INSTRUCTION_LINES:
        if line == "":
            lines.append("")
        elif remaining <= 0:
            lines.append("")
        elif remaining >= len(line):
            lines.append(line)
            remaining -= len(line)
        else:
            lines.append(line[:remaining])
            remaining = 0
    return lines


def draw_intro_screen(surface):
    def blit_centered_scaled(image, target_surface):
        image_width, image_height = image.get_size()
        target_ratio = WIDTH / HEIGHT
        image_ratio = image_width / image_height

        if image_ratio > target_ratio:
            new_width = WIDTH
            new_height = int(WIDTH / image_ratio)
        else:
            new_height = HEIGHT
            new_width = int(HEIGHT * image_ratio)

        scaled_image = pygame.transform.smoothscale(image, (new_width, new_height))
        rect = scaled_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        target_surface.blit(scaled_image, rect)

    if intro_state == "thumbnail":
        surface.fill((0, 0, 0))
        blit_centered_scaled(thumbnail_image, surface)
        return

    if intro_state == "transition_to_instructions":
        surface.fill((0, 0, 0))
        blit_centered_scaled(thumbnail_image, surface)
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(intro_transition_alpha)
        surface.blit(overlay, (0, 0))
        return

    if intro_state == "transition_to_playing":
        surface.fill((0, 0, 0))

        y = HEIGHT // 2 - 90
        for line in INSTRUCTION_LINES:
            if line == "":
                y += 24
                continue
            text_surface = intro_font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(WIDTH // 2, y))
            surface.blit(text_surface, text_rect)
            y += 42

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(intro_transition_alpha)
        surface.blit(overlay, (0, 0))
        return

    surface.fill((0, 0, 0))
    instruction_lines = _revealed_instruction_lines()

    y = HEIGHT // 2 - 90
    for line in instruction_lines:
        if line == "":
            y += 24
            continue
        text_surface = intro_font.render(line, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WIDTH // 2, y))
        surface.blit(text_surface, text_rect)
        y += 42


# --- load sprites -----------------------------------------------------
sprites = {
    "front": pygame.image.load(resource_path("assets/sprites/character-front.png")).convert_alpha(),
    "back": pygame.image.load(resource_path("assets/sprites/character-back.png")).convert_alpha(),
    "left": pygame.image.load(resource_path("assets/sprites/character-left.png")).convert_alpha(),
    "right": pygame.image.load(resource_path("assets/sprites/character-right.png")).convert_alpha(),
}

player = Player(WIDTH / 2, HEIGHT / 2, sprites)
dialogue_box = DialogueBox()
courtroom_battle_ui = courtroom_battle.CourtroomBattle()

# boss_keys listed here fight a courtroom trial instead of the boss_battle
# placeholder. The trial data lives in courtroom_battle.TRIALS under
# f"{boss_key}_trial".
TRIAL_BOSS_KEYS = {"guardian"}

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


def _after_guardian_trial():
    def _finish():
        player.center_on_screen(WIDTH, HEIGHT)

    try:
        start_transport_segment(
            dialogue_box,
            transport_id="stargate",
            destination_planet="nova",
            on_complete=_finish,
        )
    except Exception:
        _finish()


def _guardian_trial_failed():
    # Called when the player runs out of Resolve during the trial.
    dialogue_box.start(
        "Guardian",
        ["The Guardian remains unconvinced.", "Gather stronger evidence and return."],
    )


running = True
dt = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

        if intro_state != "playing":
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if intro_state == "thumbnail":
                    intro_state = "transition_to_instructions"
                    intro_timer = 0.0
                    intro_transition_alpha = 0
                elif intro_state == "instructions":
                    revealed_total = INSTRUCTION_TOTAL_CHARS if instructions_skip_typing else min(
                        INSTRUCTION_TOTAL_CHARS, int(intro_timer * INSTRUCTION_CHARS_PER_SECOND))
                    if revealed_total < INSTRUCTION_TOTAL_CHARS:
                        instructions_skip_typing = True
                    else:
                        intro_state = "transition_to_playing"
                        intro_timer = 0.0
                        intro_transition_alpha = 0
                        instructions_skip_typing = False
                else:
                    intro_state = "playing"
            continue

        if courtroom_battle_ui.active:
            courtroom_battle_ui.handle_event(event)
            continue

        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            if dialogue_box.active:
                dialogue_box.advance()
            else:
                # look for a nearby NPC to start talking to
                current_room_data = planet_manager.get_current_room_data()
                for npc in current_room_data["npcs"]:
                    if npc.is_near(player.pos):
                        lines, triggers_battle = npc.get_dialogue()

                        def _start_battle(boss_key=npc.boss_key or "guardian"):
                            if boss_key in TRIAL_BOSS_KEYS:
                                courtroom_battle_ui.start(
                                    f"{boss_key}_trial",
                                    on_complete=_after_guardian_trial,
                                    on_fail=_guardian_trial_failed,
                                )
                            else:
                                boss_battle.start_boss_battle(dialogue_box, boss_key=boss_key)

                        dialogue_box.start(
                            npc.name, lines,
                            on_complete=_start_battle if triggers_battle else None,
                        )
                        break

    if not running:
        break

    if intro_state != "playing":
        if intro_state == "thumbnail":
            intro_timer += dt
            if intro_timer >= thumbnail_duration:
                intro_state = "transition_to_instructions"
                intro_timer = 0.0
                intro_transition_alpha = 0
        elif intro_state == "transition_to_instructions":
            intro_timer += dt
            intro_transition_alpha = int(min(255, (intro_timer / transition_duration) * 255))
            if intro_timer >= transition_duration:
                intro_state = "instructions"
                intro_timer = 0.0
                intro_transition_alpha = 255
                instructions_skip_typing = False
        elif intro_state == "instructions":
            intro_timer += dt
            if intro_timer >= instructions_duration:
                intro_state = "transition_to_playing"
                intro_timer = 0.0
                intro_transition_alpha = 0
                instructions_skip_typing = False
        else:
            intro_timer += dt
            intro_transition_alpha = int(min(255, (intro_timer / transition_duration) * 255))
            if intro_timer >= transition_duration:
                intro_state = "playing"

        draw_intro_screen(screen)
        pygame.display.flip()
        dt = clock.tick(FPS) / 1000
        continue

    dialogue_box.update(dt)

    keys = pygame.key.get_pressed()

    room = planet_manager.get_current_room_data()
    if not dialogue_box.active and not courtroom_battle_ui.active and not transition_state["active"]:
        obstacles = list(room.get("obstacles", []))
        sky = room.get("sky")
        if sky:
            obstacles.append(pygame.Rect(0, 0, WIDTH, sky["height"]))

        # Auto-add mask-based obstacles for trees, rocks, and solid decor
        decor_obstacle_types = {"tree1", "tree2", "tree3", "rock", "catbuilding", "bunnybuilding"}
        mask_obstacles = []
        for item in room.get("decor", []):
            t = item.get("type")
            if t in decor_obstacle_types:
                result = background.get_collision_mask(item)
                if result is not None:
                    mask_obstacles.append(result)

        for npc in room.get("npcs", []):
            result = npc.get_collision_mask()
            if result is not None:
                mask_obstacles.append(result)
                
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
            mask_obstacles,
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
    world_surface.fill(room["color"])
    sky = room.get("sky")
    if sky:
        pygame.draw.rect(world_surface, sky["color"], pygame.Rect(0, 0, WIDTH, sky["height"]))
    background.draw_room_background(world_surface, room)

    for item in room.get("decor", []):
        background.draw(world_surface, item)

    for npc in room["npcs"]:
        npc.draw(world_surface)

    player.draw(world_surface)

    vision.apply_vision_zoom(screen, world_surface, player.pos, WIDTH, HEIGHT, coverage=0.7)

    dialogue_box.draw(screen)
    courtroom_battle_ui.draw(screen)

    if transition_state["active"]:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(int(transition_state["alpha"]))
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

    pygame.display.flip()
    dt = clock.tick(FPS) / 1000

pygame.quit()