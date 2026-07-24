class GameState:
    def __init__(self):
        self.clues = set()

    def collect(self, clue_id):
        self.clues.add(clue_id)

    def has(self, clue_id):
        return clue_id in self.clues

    def has_all(self, required_ids):
        return set(required_ids).issubset(self.clues)


game_state = GameState()