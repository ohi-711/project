import pygame
from npc import NPC
from rooms import rooms as home_rooms, room_connections as home_connections

PLANETS = {
    "home": {
        "display_name": "Home World",
        "rooms": home_rooms,
        "connections": home_connections,
        "start_room": "room1",
    },
    "nova": {
        "display_name": "Nova Prime",
        "rooms": {
            "nova1": {
                "color": (24, 40, 80),
                "name": "Nova Landing",
                "sky": {"height": 160, "color": (140, 200, 255)},
                "decor": [
                    {"type": "star", "x": 140, "y": 90, "size": 12},
                    {"type": "star", "x": 300, "y": 120, "size": 10},
                    {"type": "cloud", "x": 60, "y": 40},
                    {"type": "cloud", "x": 380, "y": 80},
                    {"type": "cloud", "x": 680, "y": 50},
                    {"type": "cloud", "x": 950, "y": 90},
                    {"type": "cloud", "x": 1150, "y": 30},
                    {"type": "rock", "x": 420, "y": 420, "size": 80},
                ],
                "obstacles": [
                    pygame.Rect(420, 420, 80, 80),
                ],
                "npcs": [
                    NPC(640, 380, "Nova Guide", (180, 230, 240),
                        ["Welcome to Nova Prime.", "The surface here is strange but safe."],
                        image_path="assets/sprites/npc_blob.gif", image_size=(42, 54),
                        repeat_lines=["Use the teleporter to explore the other sectors."],
                    ),
                ],
            },
            "nova2": {
                "color": (24, 80, 50),
                "name": "Crystal Vale",
                "sky": {"height": 120, "color": (160, 220, 190)},
                "decor": [
                    {"type": "cloud", "x": 90, "y": 80},
                    {"type": "cloud", "x": 320, "y": 40},
                    {"type": "cloud", "x": 600, "y": 60},
                    {"type": "cloud", "x": 880, "y": 30},
                    {"type": "cloud", "x": 1120, "y": 70},
                    {"type": "rock", "x": 240, "y": 420, "size": 80},
                    {"type": "rock", "x": 680, "y": 260, "size": 72},
                ],
                "obstacles": [
                    pygame.Rect(240, 420, 80, 80),
                    pygame.Rect(680, 260, 72, 72),
                ],
                "npcs": [],
            },
            "nova3": {
                "color": (70, 20, 30),
                "name": "Warp Hangar",
                "sky": {"height": 180, "color": (60, 120, 160)},
                "decor": [
                    {"type": "star", "x": 120, "y": 60, "size": 9},
                    {"type": "cloud", "x": 80, "y": 40},
                    {"type": "cloud", "x": 300, "y": 90},
                    {"type": "cloud", "x": 560, "y": 30},
                    {"type": "cloud", "x": 830, "y": 70},
                    {"type": "cloud", "x": 1080, "y": 50},
                    {"type": "rock", "x": 520, "y": 420, "size": 96},
                ],
                "obstacles": [
                    pygame.Rect(520, 420, 96, 96),
                ],
                "npcs": [
                    NPC(700, 350, "Hangar AI", (150, 200, 220),
                        ["The Stargate brought you here.", "Your next destination awaits."],
                        image_path="assets/sprites/npc_blob.gif", image_size=(42, 54),
                        repeat_lines=["Step into the gate when you are ready."],
                    ),
                ],
            },
        },
        "connections": {
            "nova1": {"left": None, "right": "nova2", "up": None, "down": None},
            "nova2": {"left": "nova1", "right": "nova3", "up": None, "down": None},
            "nova3": {"left": "nova2", "right": None, "up": None, "down": None},
        },
        "start_room": "nova1",
    },
}

current_planet = "home"
current_room = PLANETS[current_planet]["start_room"]


def get_current_room_data():
    return PLANETS[current_planet]["rooms"][current_room]


def get_current_connections():
    return PLANETS[current_planet]["connections"]


def switch_planet(planet_key, start_room=None):
    global current_planet, current_room
    if planet_key not in PLANETS:
        raise ValueError(f"Unknown planet: {planet_key}")
    current_planet = planet_key
    current_room = start_room or PLANETS[planet_key]["start_room"]


def set_current_room(room_key):
    global current_room
    current_room = room_key
    if room_key not in PLANETS[current_planet]["rooms"]:
        raise ValueError(f"Unknown room for planet {current_planet}: {room_key}")