BOSS_DIALOGUE = {
    "guardian": [
        "The ground shakes as a shadow rises before you...",
        "(Boss battle would start here!)",
        "You strike true. The Guardian falls.",
        "You have proven yourself worthy.",
    ],
}


from transport import start_transport_dialogue


def start_boss_battle(dialogue_box, boss_key="guardian", on_complete=None):
    """Start the named boss battle dialogue sequence.

    When the boss dialogue finishes, optionally call `on_complete`.
    For example, we use this to start the transport unlock dialogue.
    """
    lines = BOSS_DIALOGUE.get(boss_key)
    if lines is None:
        raise ValueError(f"Unknown boss battle key: {boss_key}")

    # when boss dialogue finishes, unlock transport and show its dialogue
    def _after_boss():
        # start transport dialogue for this boss (if any)
        try:
            start_transport_dialogue(dialogue_box, "stargate")
        except Exception:
            pass
        if on_complete:
            on_complete()

    dialogue_box.start("???", list(lines), on_complete=_after_boss)
