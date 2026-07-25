import pygame
from npc import NPC

rooms = {
    "room1": {
        "color": (80, 50, 110),
        "name": "Starting Room",
        "sky": {"height": 200, "color": (100, 170, 240)},
        "decor": [
            {"type": "cloud", "x": 80, "y": 80},
            {"type": "star", "x": 90, "y": 60, "size": 10},
            {"type": "star", "x": 180, "y": 90, "size": 8},
            {"type": "star", "x": 280, "y": 75, "size": 9},
            {"type": "star", "x": 270, "y": 50, "size": 10},
            {"type": "star", "x": 460, "y": 80, "size": 8},
            {"type": "star", "x": 560, "y": 75, "size": 11},
            {"type": "star", "x": 660, "y": 60, "size": 7},
            {"type": "star", "x": 780, "y": 110, "size": 10},
            {"type": "star", "x": 890, "y": 100, "size": 9},
            {"type": "star", "x": 960, "y": 90, "size": 8},
            {"type": "star", "x": 1020, "y": 60, "size": 10},
            {"type": "rock", "x": 300, "y": 420, "size": 64},
            {"type": "rock", "x": 620, "y": 220, "size": 48},
        ],
        "obstacles": [
            pygame.Rect(300, 420, 64, 64),
            pygame.Rect(620, 220, 48, 48),
        ],
        "npcs": [
            NPC(500, 400, "Old Slime", (200, 170, 100),
                ["Ah, a traveler.", "Take this torn map fragment — you'll need it."],
                image_path="assets/sprites/npc_blob.gif", image_size=(42, 54),
                clue_id="map_fragment",
                repeat_lines=["Safe travels. Head east to reach the Sky Room."]),

            NPC(750, 250, "Hooded Slime", (120, 90, 90),
                ["Psst... take this rusted key.", "Don't let anyone see it."],
                image_path="assets/sprites/npc_blob.gif", image_size=(42, 54),
                clue_id="rusted_key",
                repeat_lines=["Keep that key safe."]),
        ],
    },
    "room2": {
        "color": (50, 90, 130),
        "name": "Sky Room",
        "sky": {"height": 200, "color": (100, 170, 240)},
        "decor": [
            {"type": "cloud", "x": 120, "y": 80},
            {"type": "cloud", "x": 760, "y": 60},
            {"type": "star", "x": 80, "y": 60, "size": 10},
            {"type": "star", "x": 180, "y": 90, "size": 8},
            {"type": "star", "x": 280, "y": 70, "size": 9},
            {"type": "star", "x": 360, "y": 50, "size": 10},
            {"type": "star", "x": 460, "y": 95, "size": 8},
            {"type": "star", "x": 560, "y": 80, "size": 11},
            {"type": "star", "x": 660, "y": 60, "size": 7},
            {"type": "star", "x": 760, "y": 110, "size": 10},
            {"type": "star", "x": 860, "y": 70, "size": 9},
            {"type": "star", "x": 960, "y": 95, "size": 8},
            {"type": "star", "x": 1060, "y": 60, "size": 10},
        ],
        "npcs": [
            NPC(700, 300, "Cloud Slime", (230, 230, 230),
                ["Fancy some cloud silk?", "Actually... take this ancient coin, on the house."],
                image_path="assets/sprites/npc_blob.gif", image_size=(42, 54),
                clue_id="ancient_coin",
                repeat_lines=["Come back anytime."]),
        ],
    },
    "room3": {
        "color": (70, 110, 80),
        "name": "Cave Room",
        "npcs": [
            NPC(600, 350, "Guardian", (180, 40, 40), size=(48, 64),
                lines=["You lack the relics needed to pass.",
                       "Return when you've gathered them all."],
                required_clues=["map_fragment", "rusted_key", "ancient_coin"],
                on_all_clues_lines=["So... you've gathered them all.",
                                     "Let's see if you're truly worthy.",
                                     "Prepare yourself!"],
                boss_key="guardian"),
        ],
    },
    "room4": {
        "color": (50, 90, 80),
        "name": "Grass Room",
        "npcs": [],
    },
}

room_connections = {
    "room1": {"left": None, "right": "room2", "up": None, "down": "room4"},
    "room2": {"left": "room1", "right": None, "up": None, "down": "room3"},
    "room3": {"left": "room4", "right": None, "up": "room2", "down": None},
    "room4": {"left": None, "right": "room3", "up": "room1", "down": None},
}