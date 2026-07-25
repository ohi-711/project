class GameState:
    def __init__(self):
        self.clues = set()
        self.transports = set()

    def collect(self, clue_id):
        self.clues.add(clue_id)

    def has(self, clue_id):
        return clue_id in self.clues

    def has_all(self, required_ids):
        return set(required_ids).issubset(self.clues)

    def unlock_transport(self, transport_id):
        self.transports.add(transport_id)

    def has_transport(self, transport_id):
        return transport_id in self.transports


game_state = GameState()