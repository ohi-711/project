BOSS_DIALOGUE = {
    "guardian": [
        "The ground shakes as a shadow rises before you...",
        "(Boss battle would start here!)",
        "You strike true. The Guardian falls.",
        "You have proven yourself worthy.",
    ],
}


from transport import start_transport_segment


def start_boss_battle(dialogue_box, boss_key="guardian", on_complete=None):
    lines = BOSS_DIALOGUE.get(boss_key)
    if lines is None:
        raise ValueError(f"Unknown boss battle key: {boss_key}")
    
    def _after_boss():
        try:
            start_transport_segment(
                dialogue_box,
                transport_id="stargate",
                destination_planet="nova",
                on_complete=on_complete,
            )
        except Exception:
            if on_complete:
                on_complete()

    dialogue_box.start("???", list(lines), on_complete=_after_boss)
