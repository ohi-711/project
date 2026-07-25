BOSS_DIALOGUE = {
    "guardian": [
        "The ground shakes as a shadow rises before you...",
        "(Boss battle would start here!)",
        "You strike true. The Guardian falls.",
        "You have proven yourself worthy.",
    ],
}


def start_boss_battle(dialogue_box, boss_key="guardian"):
    lines = BOSS_DIALOGUE.get(boss_key)
    if lines is None:
        raise ValueError(f"Unknown boss battle key: {boss_key}")

    dialogue_box.start("???", list(lines))
