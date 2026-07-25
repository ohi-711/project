from dialogue import DialogueBox
from game_state import game_state

TRANSPORT_DIALOGUE = {
    "stargate": [
        "A shimmering gateway opens before you...",
        "You have unlocked the Stargate — travel to distant planets is now possible.",
        "Use the teleportation console to choose your destination.",
    ],
}


def unlock_transport(transport_id):
    game_state.unlock_transport(transport_id)


def start_transport_dialogue(dialogue_box: DialogueBox, transport_id: str):
    lines = TRANSPORT_DIALOGUE.get(transport_id)
    if not lines:
        lines = ["You have unlocked a new transport."]
    # mark unlocked and show dialogue
    unlock_transport(transport_id)
    dialogue_box.start("SYSTEM", list(lines))
