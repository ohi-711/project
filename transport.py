from dialogue import DialogueBox
from game_state import game_state
import planet_manager

TRANSPORT_DIALOGUE = {
    "stargate": [
        "A shimmering gateway opens before you...",
        "You have unlocked the Stargate — travel to distant planets is now possible.",
        "Destination: Nova Prime. Hold on tight.",
    ],
    "arrival_nova": [
        "The Stargate settles around you.",
        "You have arrived on Nova Prime.",
        "Explore the new rooms and find the teleporter back home.",
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


def start_transport_segment(dialogue_box: DialogueBox, transport_id: str, destination_planet: str, on_complete=None):
    unlock_transport(transport_id)
    lines = TRANSPORT_DIALOGUE.get(transport_id)
    if not lines:
        lines = ["You are traveling to a new planet."]

    def _after_launch():
        planet_manager.switch_planet(destination_planet)
        start_transport_dialogue(dialogue_box, f"arrival_{destination_planet}")
        if on_complete:
            on_complete()

    dialogue_box.start("SYSTEM", list(lines), on_complete=_after_launch)
