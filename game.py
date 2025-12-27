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
        # 1. Calculate the Optimal Move
        best_move = self.ai.find_move(self.human)
        
        # 2. Simulate: Does this move cause a 3rd repetition?
        # We need to simulate the state that WOULD happen.
        # Cloning players is tricky without side effects, but we can do a poor man's check
        # by checking if a similar sequence happened recently?
        # A simpler way: Clone the Game Logic temporarily?
        # stick.py Player copy constructor handles logical copy.
        
        # Create hypothetical future state
        ai_copy = Player(self.ai)
        human_copy = Player(self.human)
        
        # Apply the best move to copies
        # Note: ai_move() in stick.py usually targets opponent.
        # stick.py: mover.make_move(opponent, move, None)
        try:
             ai_copy.make_move(human_copy, best_move, None)
        except:
             # If best_move fails for some reason, just return it and let real game fail
             return best_move
             
        # Future state tuple
        # note: turn would flip to 0 (human)
        future_state = (
            human_copy.left_hand.fingers_up(),
            human_copy.right_hand.fingers_up(),
            ai_copy.left_hand.fingers_up(),
            ai_copy.right_hand.fingers_up(),
            0 # Future turn is human
        )
        
        # Check repetition count
        # If this exact state is already in history 2 or more times, adding it again makes 3 -> Draw.
        # So we want to avoid it if count >= 2.
        repetition_count = self.history.count(future_state)
        
        if repetition_count >= 2:
            print(f"[Auto-Divergence] Detected imminent loop with move {best_move}. Picking random alternative.")
            # Diverge! Pick a random suboptimal move.
            possible_moves = self.ai.find_moves(self.human)
            # Filter out the "bad" move if we have options, or just pick random.
            if len(possible_moves) > 1:
                # Try to find one that isn't the best_move
                alternatives = [m for m in possible_moves if m != best_move]
                if alternatives:
                    return random.choice(alternatives)
                    
            # If only 1 move exists, we are forced to draw.
            return best_move
            
        return best_move

    def next_turn(self):
        self.turn ^= 1

    def winner(self):
        if self.human.checkLoss(): return 1     # AI wins
        if self.ai.checkLoss():    return 0     # You win
        return None
