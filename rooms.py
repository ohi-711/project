from npc import NPC

rooms = {
    "room1": {
        "color": (140, 90, 180),
        "name": "Starting Room",
        "decor": [
            {"type": "cloud", "x": 80, "y": 80},
        ],
        "npcs": [
            NPC(500, 400, "Old Man", (200, 170, 100),
                ["Ah, a traveler.", "Head east to reach the Sky Room."]),
        ],
    },
    "room2": {
        "color": (90, 140, 200),
        "name": "Sky Room",
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
            NPC(700, 300, "Cloud Merchant", (230, 230, 230),
                ["Fancy some cloud silk?", "It's very light."]),
        ],
    },
    "room3": {
        "color": (70, 110, 80),
        "name": "Cave Room",
        "decor": [
            {"type": "star", "x": 600, "y": 90, "size": 8},
        ],
        "npcs": [],
    },
}

room_connections = {
    "room1": {"left": None, "right": "room2", "up": None, "down": None},
    "room2": {"left": "room1", "right": None, "up": None, "down": "room3"},
    "room3": {"left": None, "right": None, "up": "room2", "down": None},
}