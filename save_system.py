"""
Saves are plain JSON files written to a folder in the user's home directory
this module knows how to persist/retrieve the dict per slot.
"""

import json
import os
from pathlib import Path

NUM_SLOTS = 3

SAVE_DIR = Path(os.path.expanduser("~")) / ".space_detective_saves"


def _slot_path(slot):
    return SAVE_DIR / f"save_slot_{slot}.json"


def ensure_save_dir():
    SAVE_DIR.mkdir(parents=True, exist_ok=True)


def save_exists(slot):
    return _slot_path(slot).exists()


def save_game(slot, data):
    """Writes `data` (a JSON-serializable dict) to the given slot (1-based).
    Returns True on success, False if writing failed for any reason."""
    try:
        ensure_save_dir()
        with open(_slot_path(slot), "w") as save_file:
            json.dump(data, save_file)
        return True
    except OSError:
        return False


def load_game(slot):
    """Returns the saved dict for `slot`, or None if the slot is empty or
    the save file is missing/corrupt."""
    path = _slot_path(slot)
    if not path.exists():
        return None
    try:
        with open(path, "r") as save_file:
            return json.load(save_file)
    except (OSError, json.JSONDecodeError):
        return None


def delete_save(slot):
    path = _slot_path(slot)
    if path.exists():
        try:
            path.unlink()
        except OSError:
            pass


def get_slot_summary(slot):
    """Short human-readable description of what's in a slot, e.g.
    "home - room2", or None if the slot is empty/unreadable."""
    data = load_game(slot)
    if not data:
        return None
    planet = data.get("planet", "?")
    room = data.get("room", "?")
    return f"{planet} - {room}"