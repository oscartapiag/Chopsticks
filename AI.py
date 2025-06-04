from stick import Player

class AI(Player):
    inf = float("inf")
    winning_val = 1000000

    def __init__(self, difficulty, AI = None):
        super().__init__(AI)
        self.lastMove = None
        self.DEPTH = difficulty

    def find_move(self, opponent: Player):
        AI_copy = AI(self.DEPTH, self)
        opponent_copy = Player(opponent)
        self.lastMove = None
        self.min_max(AI_copy, opponent_copy, self.DEPTH, 1, True, -AI.inf, AI.inf)
        return self.lastMove

    def min_max(self, ai, opponent: Player, depth, sense, save_move, alpha, beta):
        if depth == 0 or opponent.checkLoss() or ai.checkLoss():
            return ai.score(opponent, sense, AI.winning_val + depth)
        possible_moves = ai.find_moves(opponent)
        if len(possible_moves) == 0:
            raise Exception("There should always be a possible move")
        best_move = None
        if sense == 1:
            bestScore = -AI.inf
            for move in possible_moves:
                AI_copy = AI(self.DEPTH, ai)
                opponent_copy = Player(opponent)
                AI_copy.make_move(opponent_copy, move, None)
                score = self.min_max(opponent_copy, AI_copy, depth - 1, -1,  False, alpha, beta)
                if score > bestScore:
                    bestScore = score
                    alpha = max(alpha, bestScore)
                    best_move = move
                    if beta <= alpha:
                        break
        else:
            bestScore = AI.inf
            for move in possible_moves:
                AI_copy = AI(self.DEPTH, ai)
                opponent_copy = Player(opponent)
                AI_copy.make_move(opponent_copy, move, None)
                score = self.min_max(opponent_copy, AI_copy, depth - 1, 1, False, alpha, beta)
                if score < bestScore:
                    bestScore = score
                    beta = min(beta, bestScore)
                    best_move = move
                    if beta <= alpha:
                        break
        if save_move:
            self.lastMove = best_move
        return bestScore
