"""
Courtroom "trial" battle system.

Instead of a straight fight, the player cross-examines a witness:

  1. Witness gives an intro, then testimony one statement at a time.
  2. On each statement the player can:
       - PRESS   -> ask for more detail (reveals a follow-up line, no risk)
       - PRESENT -> pick a piece of evidence from game_state.clues and
                    present it against the current statement
  3. Presenting the *correct* evidence cracks the statement and damages
     the witness's Composure meter. Presenting the wrong evidence damages
     the player's Resolve meter instead.
  4. Composure hits 0  -> player wins the trial (on_complete callback).
     Resolve hits 0     -> player loses the trial (on_fail callback).

This mirrors the shape of boss_battle.py (a data table + a start_* entry
point) but needs its own small state machine and its own draw()/handle_event()
because it's menu-driven rather than a simple line-advance dialogue.

--- Wiring into main.py (not done automatically) ---
    import courtroom_battle
    trial_battle = courtroom_battle.CourtroomBattle()

    # in the event loop, before/instead of the dialogue_box.advance() branch:
    if trial_battle.active:
        trial_battle.handle_event(event)

    # skip player movement while a trial is active, same as dialogue_box.active:
    if not dialogue_box.active and not trial_battle.active and not transition_state["active"]:
        ...

    # in the draw section, after dialogue_box.draw(screen):
    trial_battle.draw(screen)

    # to kick one off (e.g. instead of boss_battle.start_boss_battle):
    trial_battle.start(
        "guardian_trial",
        on_complete=lambda: player.center_on_screen(WIDTH, HEIGHT),
        on_fail=lambda: dialogue_box.start("SYSTEM", ["The Guardian remains unconvinced."]),
    )
"""

import pygame
from settings import WIDTH, HEIGHT, DIALOGUE_BG, DIALOGUE_BORDER, WHITE
from game_state import game_state

# Display names for clues so they read like courtroom exhibits rather than
# raw ids. Extend this alongside any new clue_ids you add in rooms.py.
EVIDENCE_NAMES = {
    "map_fragment": "Torn Map Fragment",
    "rusted_key": "Rusted Key",
    "ancient_coin": "Ancient Coin",
}

MAX_RESOLVE = 100
MAX_COMPOSURE = 100
WRONG_EVIDENCE_DAMAGE = 25
CORRECT_EVIDENCE_DAMAGE = 40


# Each statement can define:
#   text             - the line as first shown
#   pressed_text     - extra detail shown once the player Presses it
#   contradiction    - the clue_id that contradicts this statement
#   success_lines    - shown when the correct evidence is presented
TRIALS = {
    "guardian_trial": {
        "witness_name": "Court Witness: Guardian",
        "intro_lines": [
            "All rise. The trial against the Guardian is now in session.",
            "The witness will now give testimony.",
        ],
        "statements": [
            {
                "text": "I have stood at this gate since before you were born.",
                "pressed_text": "No one has ever passed... until now.",
                "contradiction": "map_fragment",
                "success_lines": [
                    "This map fragment proves passage was charted before!",
                    "The witness recoils. That's one crack in the story.",
                ],
            },
            {
                "text": "No key exists that could open the old vault.",
                "pressed_text": "The vault hasn't been opened in a hundred years.",
                "contradiction": "rusted_key",
                "success_lines": [
                    "Then explain this rusted key, cut for that very vault!",
                    "The witness stammers. Another crack.",
                ],
            },
            {
                "text": "This land has never traded with outsiders.",
                "pressed_text": "Not a single coin has ever left these halls.",
                "contradiction": "ancient_coin",
                "success_lines": [
                    "Then explain this ancient coin, found beyond the gate!",
                    "The witness's composure shatters completely.",
                ],
            },
        ],
        "verdict_success": [
            "The court has heard enough.",
            "You have proven your case. The Guardian stands down.",
        ],
        "verdict_fail": [
            "Your resolve falters. The court is not convinced...",
            "You'll need stronger evidence next time.",
        ],
    },
}


class CourtroomBattle:
    """Owns all trial state: which witness, which statement, meters, and
    which sub-menu (if any) is open. main.py just calls handle_event/draw."""

    def __init__(self):
        self.active = False
        self.state = None  # "queue" | "statement" | "menu" | "evidence"
        self._next_state_after_queue = None

        self.witness_name = ""
        self.statements = []
        self.verdict_success = []
        self.verdict_fail = []
        self.stmt_index = 0
        self.cracked = set()
        self.showing_pressed = False

        self.queue = []
        self.queue_pos = 0

        self.on_complete = None
        self.on_fail = None

        self.player_resolve = MAX_RESOLVE
        self.witness_composure = MAX_COMPOSURE

        self.menu_cursor = 0      # 0 = Press, 1 = Present
        self.evidence_cursor = 0

        self.font = pygame.font.SysFont(None, 30)
        self.name_font = pygame.font.SysFont(None, 26, bold=True)
        self.small_font = pygame.font.SysFont(None, 22)

        self.box_height = 200
        self.box_rect = pygame.Rect(40, HEIGHT - self.box_height - 30,
                                     WIDTH - 80, self.box_height)

    # --- public API ---------------------------------------------------

    def start(self, trial_key, on_complete=None, on_fail=None):
        trial = TRIALS.get(trial_key)
        if trial is None:
            raise ValueError(f"Unknown trial key: {trial_key}")

        self.witness_name = trial["witness_name"]
        self.statements = trial["statements"]
        self.verdict_success = trial["verdict_success"]
        self.verdict_fail = trial["verdict_fail"]

        self.stmt_index = 0
        self.cracked = set()
        self.player_resolve = MAX_RESOLVE
        self.witness_composure = MAX_COMPOSURE
        self.on_complete = on_complete
        self.on_fail = on_fail

        self.active = True
        self._start_queue(trial["intro_lines"], next_state="statement")

    def handle_event(self, event):
        if not self.active or event.type != pygame.KEYDOWN:
            return

        if self.state == "queue":
            if event.key == pygame.K_e:
                self.queue_pos += 1
                if self.queue_pos >= len(self.queue):
                    self._advance_from(self._next_state_after_queue)
            return

        if self.state == "statement":
            if event.key == pygame.K_e:
                self.state = "menu"
                self.menu_cursor = 0
            return

        if self.state == "menu":
            if event.key == pygame.K_UP:
                self.menu_cursor = (self.menu_cursor - 1) % 2
            elif event.key == pygame.K_DOWN:
                self.menu_cursor = (self.menu_cursor + 1) % 2
            elif event.key == pygame.K_e:
                if self.menu_cursor == 0:
                    self._do_press()
                else:
                    self._open_evidence_menu()
            elif event.key == pygame.K_ESCAPE:
                self.state = "statement"
            return

        if self.state == "evidence":
            available = self._available_evidence()
            if event.key == pygame.K_UP and available:
                self.evidence_cursor = (self.evidence_cursor - 1) % len(available)
            elif event.key == pygame.K_DOWN and available:
                self.evidence_cursor = (self.evidence_cursor + 1) % len(available)
            elif event.key == pygame.K_e and available:
                self._present_evidence(available[self.evidence_cursor])
            elif event.key == pygame.K_ESCAPE:
                self.state = "menu"
            return

    def draw(self, screen):
        if not self.active:
            return

        self._draw_meter(screen, 60, 40, 300, 18,
                          self.player_resolve, MAX_RESOLVE, (80, 180, 90), "Your Resolve")
        self._draw_meter(screen, WIDTH - 360, 40, 300, 18,
                          self.witness_composure, MAX_COMPOSURE, (200, 70, 70), "Witness Composure")

        pygame.draw.rect(screen, DIALOGUE_BG, self.box_rect, border_radius=10)
        pygame.draw.rect(screen, DIALOGUE_BORDER, self.box_rect, width=2, border_radius=10)

        padding = 20
        name_surf = self.name_font.render(self.witness_name, True, WHITE)
        screen.blit(name_surf, (self.box_rect.x + padding, self.box_rect.y + 12))

        text, hint = self._current_text_and_hint()
        wrapped = self._wrap_text(text, self.font, self.box_rect.width - padding * 2)
        for i, line in enumerate(wrapped):
            surf = self.font.render(line, True, WHITE)
            screen.blit(surf, (self.box_rect.x + padding, self.box_rect.y + 50 + i * 28))

        if self.state == "menu":
            for i, option in enumerate(["Press Statement", "Present Evidence"]):
                color = (255, 230, 120) if i == self.menu_cursor else WHITE
                marker = "> " if i == self.menu_cursor else "  "
                surf = self.font.render(marker + option, True, color)
                screen.blit(surf, (self.box_rect.x + padding, self.box_rect.y + 120 + i * 28))

        if self.state == "evidence":
            available = self._available_evidence()
            if not available:
                surf = self.small_font.render("(no evidence collected yet)", True, (180, 180, 180))
                screen.blit(surf, (self.box_rect.x + padding, self.box_rect.y + 120))
            else:
                for i, clue_id in enumerate(available):
                    label = EVIDENCE_NAMES.get(clue_id, clue_id)
                    color = (255, 230, 120) if i == self.evidence_cursor else WHITE
                    marker = "> " if i == self.evidence_cursor else "  "
                    surf = self.small_font.render(marker + label, True, color)
                    screen.blit(surf, (self.box_rect.x + padding, self.box_rect.y + 120 + i * 24))

        hint_surf = self.small_font.render(hint, True, (160, 160, 160))
        screen.blit(hint_surf, (self.box_rect.right - hint_surf.get_width() - padding,
                                 self.box_rect.bottom - 30))

    # --- internal state machine ---------------------------------------

    def _current_statement(self):
        return self.statements[self.stmt_index]

    def _available_evidence(self):
        return sorted(game_state.clues)

    def _start_queue(self, lines, next_state):
        self.queue = list(lines)
        self.queue_pos = 0
        self._next_state_after_queue = next_state
        self.state = "queue"

    def _do_press(self):
        self.showing_pressed = True
        self.state = "statement"

    def _open_evidence_menu(self):
        self.evidence_cursor = 0
        self.state = "evidence"

    def _present_evidence(self, clue_id):
        stmt = self._current_statement()
        if clue_id == stmt.get("contradiction") and self.stmt_index not in self.cracked:
            self.cracked.add(self.stmt_index)
            self.witness_composure -= CORRECT_EVIDENCE_DAMAGE
            self._start_queue(stmt["success_lines"], next_state="advance")
        else:
            self.player_resolve -= WRONG_EVIDENCE_DAMAGE
            self._start_queue(
                ["That doesn't contradict anything...", "The court is unimpressed."],
                next_state="check",
            )

    def _advance_from(self, tag):
        if tag == "statement":
            self.showing_pressed = False
            self.state = "statement"

        elif tag == "advance":
            if self.witness_composure <= 0:
                self._start_queue(self.verdict_success, next_state="win")
            else:
                self.stmt_index = (self.stmt_index + 1) % len(self.statements)
                self.showing_pressed = False
                self.state = "statement"

        elif tag == "check":
            if self.player_resolve <= 0:
                self._start_queue(self.verdict_fail, next_state="lose")
            else:
                self.showing_pressed = False
                self.state = "statement"

        elif tag == "win":
            self.active = False
            if self.on_complete:
                callback = self.on_complete
                self.on_complete = None
                callback()

        elif tag == "lose":
            self.active = False
            if self.on_fail:
                callback = self.on_fail
                self.on_fail = None
                callback()

    def _current_text_and_hint(self):
        if self.state == "queue":
            return self.queue[self.queue_pos], "[E] continue"

        if self.state == "statement":
            stmt = self._current_statement()
            text = stmt["pressed_text"] if self.showing_pressed and stmt.get("pressed_text") else stmt["text"]
            if self.stmt_index in self.cracked:
                text = "(cracked) " + text
            return text, "[E] Press / Present"

        if self.state == "menu":
            return self._current_statement()["text"], "[UP/DOWN] choose  [E] select  [ESC] back"

        if self.state == "evidence":
            return "Select evidence to present:", "[UP/DOWN] choose  [E] present  [ESC] back"

        return "", ""

    # --- small drawing helpers -----------------------------------------

    def _wrap_text(self, text, font, max_width):
        words = text.split(" ")
        lines, current = [], ""
        for word in words:
            test = f"{current} {word}".strip()
            if font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def _draw_meter(self, screen, x, y, w, h, value, max_value, color, label):
        pygame.draw.rect(screen, (50, 50, 50), (x, y, w, h), border_radius=4)
        fill_w = int(w * max(value, 0) / max_value)
        pygame.draw.rect(screen, color, (x, y, fill_w, h), border_radius=4)
        pygame.draw.rect(screen, WHITE, (x, y, w, h), width=1, border_radius=4)
        label_surf = self.small_font.render(label, True, WHITE)
        screen.blit(label_surf, (x, y - 20))