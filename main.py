import pygame
from settings import WIDTH, HEIGHT, FPS, DECOR_COLOR, TEXT_SPEED, INTERACT_RANGE
import planet_manager
from player import Player
from dialogue import DialogueBox
import boss_battle
import courtroom_battle
from transport import start_transport_segment
import background
import vision
import chaser
from resource_path import resource_path

pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass
screen = pygame.display.set_mode((WIDTH, HEIGHT))
world_surface = pygame.Surface((WIDTH, HEIGHT))
pygame.display.set_caption("Space Detective Game")
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

# typewriter effect for the WASD/instructions text
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

# dark figure chaser
dark_figure = chaser.DarkFigure()
dark_figure_room = None

# Where the figure appears when the player steps into each Nova room.
NOVA_CHASER_SPAWNS = {
    "nova1": (1060, 520),
    "nova2": (980, 500),
    "nova3": (180, 520),
}

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
    "mode": "room",       # "room" (walked off an edge) or "building" (walked through a door)
    "spawn_pos": None,    # used only when mode == "building"
}


def _room_play_rect(room_data):
    if room_data.get("native_size"):
        bg_path = room_data.get("background_image")
        rect = background.get_centered_rect(bg_path, WIDTH, HEIGHT) if bg_path else None
        if rect is not None:
            return rect
    return pygame.Rect(0, 0, WIDTH, HEIGHT)


def _resolve_room_pos(room_data, pos):
    if isinstance(pos, dict) and "fraction" in pos:
        play_rect = _room_play_rect(room_data)
        fx, fy = pos["fraction"]
        return (play_rect.x + fx * play_rect.width, play_rect.y + fy * play_rect.height)
    return pos


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
        "mode": "room",
        "spawn_pos": None,
    })


def request_building_transition(building):
    global transition_state
    if transition_state["active"]:
        return
    target_room_key = building["target_room"]
    target_room_data = planet_manager.PLANETS[planet_manager.current_planet]["rooms"][target_room_key]
    spawn_pos = _resolve_room_pos(target_room_data, building["spawn_pos"])
    transition_state.update({
        "active": True,
        "phase": "out",
        "alpha": 0,
        "target_room": target_room_key,
        "direction": None,
        "mode": "building",
        "spawn_pos": spawn_pos,
    })


def _follow_chaser_through_doorway(direction, gap_distance):
    """Positions the dark figure just inside the new room, coming through
    the same doorway the player used"""
    edge_offset = 20
    if direction == "left":
        # player exits left, so they land near the right edge of the next room
        x, y = WIDTH - edge_offset, player.pos.y
    elif direction == "right":
        x, y = edge_offset, player.pos.y
    elif direction == "up":
        x, y = player.pos.x, HEIGHT - edge_offset
    elif direction == "down":
        x, y = player.pos.x, edge_offset
    else:
        x, y = player.pos.x, player.pos.y

    delay = min(max(gap_distance / 200, 0.3), 2.5)
    dark_figure.spawn_with_delay(x, y, delay)


def _complete_room_change():
    global dark_figure_room

    chase_gap = None
    if planet_manager.current_planet == "nova" and dark_figure.active:
        chase_gap = dark_figure.pos.distance_to(player.pos)

    planet_manager.set_current_room(transition_state["target_room"])
    if transition_state["mode"] == "building":
        player.pos = pygame.Vector2(*transition_state["spawn_pos"])
    else:
        player.snap_to_edge(transition_state["direction"], WIDTH, HEIGHT)
    transition_state["phase"] = "in"

    if chase_gap is not None:
        _follow_chaser_through_doorway(transition_state["direction"], chase_gap)
        dark_figure_room = planet_manager.current_room


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


# captured by figure
capture_state = {"active": False, "phase": None, "alpha": 0}
CAPTURE_FADE_SPEED = 500


def _trigger_capture():
    if capture_state["active"]:
        return
    capture_state.update({"active": True, "phase": "out", "alpha": 0})


def _complete_capture():
    global dark_figure_room
    nova_start_room = planet_manager.PLANETS["nova"]["start_room"]
    planet_manager.set_current_room(nova_start_room)
    player.pos = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
    player.facing = "front"
    dark_figure.deactivate()
    dark_figure_room = None
    capture_state["phase"] = "in"


def _sync_planet_music():
    """Loads and loops the current planet's music track"""
    global _current_music_planet
    if planet_manager.current_planet == _current_music_planet:
        return
    _current_music_planet = planet_manager.current_planet
    music_path = planet_manager.get_current_music_path()
    if not music_path:
        pygame.mixer.music.stop()
        return
    try:
        pygame.mixer.music.load(resource_path(music_path))
        pygame.mixer.music.play(-1)  # loop forever
    except pygame.error:
        # file missing/unreadable
        pygame.mixer.music.stop()


_current_music_planet = None

running = True
dt = 0

while running:
    _sync_planet_music()

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

        if capture_state["active"]:
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
                interacted = False
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
                        interacted = True
                        break

                # if no NPC was close enough, check for a nearby building door
                if not interacted and not transition_state["active"]:
                    for building in current_room_data.get("buildings", []):
                        door_x, door_y = _resolve_room_pos(current_room_data, building["door_pos"])
                        if pygame.Vector2(door_x, door_y).distance_to(player.pos) <= INTERACT_RANGE:
                            request_building_transition(building)
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
            # Keep the timer running (it drives the typewriter reveal), but don't auto-advance
            intro_timer += dt
        else:
            intro_timer += dt
            intro_transition_alpha = int(min(255, (intro_timer / transition_duration) * 255))
            if intro_timer >= transition_duration:
                intro_state = "playing"

        if intro_state != "playing":
            draw_intro_screen(screen)
            pygame.display.flip()
            dt = clock.tick(FPS) / 1000
            continue

    dialogue_box.update(dt)

    keys = pygame.key.get_pressed()

    room = planet_manager.get_current_room_data()

    if planet_manager.current_planet == "nova":
        if not dark_figure.active or dark_figure_room != planet_manager.current_room:
            spawn_x, spawn_y = NOVA_CHASER_SPAWNS.get(
                planet_manager.current_room, (WIDTH - 120, HEIGHT - 150)
            )
            dark_figure.spawn(spawn_x, spawn_y)
            dark_figure_room = planet_manager.current_room
    else:
        if dark_figure.active:
            dark_figure.deactivate()
        dark_figure_room = None

    if (not dialogue_box.active and not courtroom_battle_ui.active
            and not transition_state["active"] and not capture_state["active"]):
        obstacles = list(room.get("obstacles", []))
        sky = room.get("sky")
        if sky:
            obstacles.append(pygame.Rect(0, 0, WIDTH, sky["height"]))

        if room.get("native_size"):
            play_rect = _room_play_rect(room)
            obstacles.extend([
                pygame.Rect(0, 0, WIDTH, play_rect.top),                              # top wall
                pygame.Rect(0, play_rect.bottom, WIDTH, HEIGHT - play_rect.bottom),    # bottom wall
                pygame.Rect(0, play_rect.top, play_rect.left, play_rect.height),       # left wall
                pygame.Rect(play_rect.right, play_rect.top,
                             WIDTH - play_rect.right, play_rect.height),               # right wall
            ])
            # prevent player from walking up wall
            for interior_obs in room.get("interior_obstacles", []):
                fx, fy, fw, fh = interior_obs["fraction_rect"]
                obstacles.append(pygame.Rect(
                    play_rect.x + fx * play_rect.width,
                    play_rect.y + fy * play_rect.height,
                    fw * play_rect.width,
                    fh * play_rect.height,
                ))

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

        if planet_manager.current_planet == "nova":
            player_center = player.pos + pygame.Vector2(
                player.image.get_width() / 2, player.image.get_height() / 2
            )
            dark_figure.update(dt, player_center)
            if dark_figure.has_captured(player_center):
                _trigger_capture()

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
                transition_state["mode"] = "room"
                transition_state["spawn_pos"] = None

    if capture_state["active"]:
        if capture_state["phase"] == "out":
            capture_state["alpha"] += CAPTURE_FADE_SPEED * dt
            if capture_state["alpha"] >= 255:
                capture_state["alpha"] = 255
                _complete_capture()
        else:
            capture_state["alpha"] -= CAPTURE_FADE_SPEED * dt
            if capture_state["alpha"] <= 0:
                capture_state["alpha"] = 0
                capture_state["active"] = False
                capture_state["phase"] = None

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

    dark_figure.draw(world_surface)

    player.draw(world_surface)

    if planet_manager.current_planet == "nova":
        player_center = player.pos + pygame.Vector2(
            player.image.get_width() / 2, player.image.get_height() / 2
        )
        vision.apply_vision_zoom_with_darkness(screen, world_surface, player_center, WIDTH, HEIGHT,
                                                coverage=0.7, radius=140, edge_softness=60)
    else:
        vision.apply_vision_zoom(screen, world_surface, player.pos, WIDTH, HEIGHT, coverage=0.7)

    dialogue_box.draw(screen)
    courtroom_battle_ui.draw(screen)

    if transition_state["active"]:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(int(transition_state["alpha"]))
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

    if capture_state["active"]:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(int(capture_state["alpha"]))
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

    pygame.display.flip()
    dt = clock.tick(FPS) / 1000

pygame.quit()