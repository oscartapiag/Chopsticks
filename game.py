# game.py
from stick import Player
from AI import AI

class Game:
    def __init__(self, vs_ai: bool = True, depth: int = 5):
        self.human = Player()
        self.ai    = AI(depth) if vs_ai else Player()
        self.turn  = 0          # 0 = human’s turn, 1 = AI’s

    # ------------- data the GUI needs -------------
    def left (self, who):  # who = 0 (you) or 1 (AI)
        p = self.human if who == 0 else self.ai
        return p.left_hand.fingers_up()

    def right(self, who):
        p = self.human if who == 0 else self.ai
        return p.right_hand.fingers_up()

    def legal_moves(self):
        mover, opp = (self.human, self.ai) if self.turn == 0 else (self.ai, self.human)
        return mover.find_moves(opp)

    def apply_move(self, move):
        mover, opp = (self.human, self.ai) if self.turn == 0 else (self.ai, self.human)
        mover.make_move(opp, move, None)        # existing logic in stick.py:contentReference[oaicite:0]{index=0}

    def ai_move(self):
        return self.ai.find_move(self.human)    # AI.py entry point:contentReference[oaicite:1]{index=1}

    def next_turn(self):
        self.turn ^= 1

    def winner(self):
        if self.human.checkLoss(): return 1     # AI wins
        if self.ai.checkLoss():    return 0     # You win
        return None
