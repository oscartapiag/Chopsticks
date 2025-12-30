import random
from stick import Player
from AI import AI

class Game:
    def __init__(self, vs_ai: bool = True, depth: int = 5):
        self.human = Player()
        self.ai    = AI(depth) if vs_ai else Player()
        self.turn  = 0          # 0 = human’s turn, 1 = AI’s
        self.history = []       # For auto-divergence (loop detection)

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
        mover.make_move(opp, move, None)        # existing logic in stick.py
        
        # Track history to detect loops
        # State: (human_L, human_R, ai_L, ai_R, turn_indicator)
        state = (
            self.human.left_hand.fingers_up(),
            self.human.right_hand.fingers_up(),
            self.ai.left_hand.fingers_up(),
            self.ai.right_hand.fingers_up(),
            self.turn
        )
        self.history.append(state)

    def ai_move(self):
        # Calculate the Optimal Move
        return self.ai.find_move(self.human)

    def next_turn(self):
        self.turn ^= 1

    def winner(self):
        if self.human.checkLoss(): return 1     # AI wins
        if self.ai.checkLoss():    return 0     # You win
        
        # Check Stalemate (Loop)
        if self.checkStalemate():
            # Sudde Death: Most fingers wins
            h_total = self.human.left_hand.fingers_up() + self.human.right_hand.fingers_up()
            a_total = self.ai.left_hand.fingers_up() + self.ai.right_hand.fingers_up()
            
            if h_total > a_total: return 2  # Human wins (Stalemate)
            if a_total > h_total: return 3  # AI wins (Stalemate)
            return -1 # True Tie (rare)
            
        return None

    def checkStalemate(self):
        if not self.history: return False
        current_state = self.history[-1]
        # Only look at the last 16 moves (approx 4 moves/loop * 3 reps + buffer)
        recent_history = self.history[-16:]
        return recent_history.count(current_state) >= 3
