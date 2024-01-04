from stick import Player

class AI(Player):
    DEPTH = 5
    inf = float("inf")

    def find_move(self, opponent: Player):
        pass

    def min_max(self, opponent: Player, depth, sense, alpha, beta):
        if depth == 0 or opponent.checkLoss() or self.checkLoss():
            return self.score()


    def score(self, opponent: Player):
        if opponent.checkLoss(): return AI.inf
        if self.checkLoss(): return -AI.inf
        AI_total = self.left_hand.fingers_up() + self.right_hand.fingers_up()
        opp_total = opponent.left_hand.fingers_up() + opponent.right_hand.fingers_up()
        return AI_total - opp_total