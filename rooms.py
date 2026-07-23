from npc import NPC

rooms = {
    "room1": {
        "color": (140, 90, 180),
        "name": "Starting Room",
        "decor": [(180, 140, 100, 100), (900, 180, 120, 120)],
        "npcs": [
            NPC(500, 400, "Old Man", (200, 170, 100),
                ["Ah, a traveler.", "Head east to reach the Sky Room."]),
        ],
    },
    "room2": {
        "color": (90, 140, 200),
        "name": "Sky Room",
        "decor": [(240, 320, 140, 90), (940, 120, 80, 180)],
        "npcs": [
            NPC(700, 300, "Cloud Merchant", (230, 230, 230),
                ["Fancy some cloud silk?", "It's very light."]),
        ],
    },
    "room3": {
        "color": (70, 110, 80),
        "name": "Cave Room",
        "decor": [(420, 240, 110, 110), (860, 430, 140, 90)],
        "npcs": [],
    },
}

room_connections = {
    "room1": {"left": None, "right": "room2", "up": None, "down": None},
    "room2": {"left": "room1", "right": None, "up": None, "down": "room3"},
    "room3": {"left": None, "right": None, "up": "room2", "down": None},
}