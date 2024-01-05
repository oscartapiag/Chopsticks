from stick import Player

class AI(Player):
    DEPTH = 4
    inf = float("inf")

    def __init__(self):
        super().__init__()
        self.lastMove = None

    def make_move(self, opponent: Player, move):
        if not move:
            raise Exception("No move found :(")
        m0 = move[0]
        m1 = move[1]
        if m0 == "l":
            if m1 == "l":
                opponent.hit(self.left_hand.fingers_up(), True)
            if m1 == "r":
                opponent.hit(self.left_hand.fingers_up(), False)
        if m0 == "r":
            if m1 == "l":
                opponent.hit(self.right_hand.fingers_up(), True)
            if m1 == "r":
                opponent.hit(self.right_hand.fingers_up(), False)
        if m0 == "s":
            if m1 == "l":
                self.split(True)
            if m1 == "r":
                self.split(False)

    def find_move(self, opponent: Player):
        opponent_left_hand_fingers = opponent.left_hand.fingers_up()
        opponent_right_hand_fingers = opponent.right_hand.fingers_up()
        AI_left_hand_fingers = self.left_hand.fingers_up()
        AI_right_hand_fingers = self.right_hand.fingers_up()
        self.min_max(opponent, AI.DEPTH, 1, True, -AI.inf, AI.inf)
        opponent.left_hand.update_hand(opponent_left_hand_fingers)
        opponent.right_hand.update_hand(opponent_right_hand_fingers)
        self.left_hand.update_hand(AI_left_hand_fingers)
        self.right_hand.update_hand(AI_right_hand_fingers)
        return self.lastMove

    def min_max(self, opponent: Player, depth, sense, save_move, alpha, beta):
        if depth == 0 or opponent.checkLoss() or self.checkLoss():
            return self.score(opponent)
        possible_moves = self.find_moves(opponent)
        best_move = None
        if sense == 1:
            bestScore = -AI.inf
            for move in possible_moves:
                self.make_move(opponent, move)
                score = self.min_max(opponent, depth - 1, -1,  False, alpha, beta)
                if score > bestScore:
                    bestScore = score
                    alpha = max(alpha, bestScore)
                    best_move = move
                    if beta <= alpha:
                        return bestScore
        else:
            bestScore = AI.inf
            for move in possible_moves:
                self.make_move(opponent, move)
                score = self.min_max(opponent, depth - 1, 1, False, alpha, beta)
                if score < bestScore:
                    bestScore = score
                    beta = min(beta, bestScore)
                    best_move = move
                    if beta <= alpha:
                        return bestScore
        if save_move:
            self.lastMove = best_move
        return bestScore

    def find_moves(self, opponent: Player):
        lst = []
        if self.left_hand.fingers_up() > 0:
            if opponent.left_hand.fingers_up() > 0:
                lst.append("ll")
            if opponent.right_hand.fingers_up() > 0:
                lst.append("lr")
        if self.right_hand.fingers_up() > 0:
            if opponent.left_hand.fingers_up() > 0:
                lst.append("rl")
            if opponent.right_hand.fingers_up() > 0:
                lst.append("rr")
        if self.hands_up() == 1:
            if self.right_hand.fingers_up() > 0 and self.right_hand.fingers_up() % 2 == 0:
                lst.append("sr")
            if self.left_hand.fingers_up() > 0 and self.left_hand.fingers_up() % 2 == 0:
                lst.append("sl")
        return lst
    #Adjust scoring function
    def score(self, opponent: Player):
        if opponent.checkLoss(): return AI.inf
        if self.checkLoss(): return -AI.inf
        AI_total = self.left_hand.fingers_up() + self.right_hand.fingers_up()
        opp_total = opponent.left_hand.fingers_up() + opponent.right_hand.fingers_up()
        return AI_total - opp_total