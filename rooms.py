from npc import NPC

rooms = {
    "room1": {
        "color": (140, 90, 180),
        "name": "Starting Room",
        "decor": [
            {"type": "cloud", "x": 80, "y": 80},
            {"type": "star", "x": 220, "y": 120, "size": 10},
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
            {"type": "star", "x": 900, "y": 100, "size": 12},
            {"type": "tree", "x": 120, "y": 420},
            {"type": "tree", "x": 800, "y": 350},
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