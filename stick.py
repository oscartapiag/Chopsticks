class Hand:
    def __init__(self, hand = None):
        if hand:
            self.fingers = hand.fingers[:]
        else:
            self.fingers = [True] + 4 * [False]

    def update_hand(self, num):
        if num == 0:
            self.fingers = 5 * [False]
        elif num == 1:
            self.fingers = [True] + 4 * [False]
        elif num == 2:
            self.fingers = 2 * [True] + 3 * [False]
        elif num == 3:
            self.fingers = 3 * [True] + 2 * [False]
        elif num == 4:
            self.fingers = 4 * [True] + [False]
        elif num == 5:
            self.fingers = 5 * [True]
        else:
            raise Exception("Invalid number of fingers")

    def hit_hand(self, num):
        total_fingers = (self.fingers_up() + num) % 5
        self.update_hand(total_fingers)

    def fingers_up(self):
        return len([1 for f in self.fingers if f])

class Player:
    inf = float("inf")
    def __init__(self, player = None):
        if player:
            self.left_hand = Hand(player.left_hand)
            self.right_hand = Hand(player.right_hand)
            self.hands = (self.left_hand, self.right_hand)
        else:
            self.left_hand = Hand()
            self.right_hand = Hand()
            self.hands = (self.left_hand, self.right_hand)

    def hands_up(self):
        return len([1 for h in self.hands if h.fingers_up() > 0])

    def hit(self, num, left):
        if left:
            new_total = (self.left_hand.fingers_up() + num) % 5
            self.left_hand.update_hand(new_total)
        else:
            new_total = (self.right_hand.fingers_up() + num) % 5
            self.right_hand.update_hand(new_total)

    def split(self, left):
        if self.hands_up() == 2: raise Exception("Only available when having one hand")
        if left:
            if self.left_hand.fingers_up() % 2 == 1: raise Exception("Only available when even number of fingers")
            new_fingers = self.left_hand.fingers_up() // 2
            self.left_hand.update_hand(new_fingers)
            self.right_hand.update_hand(new_fingers)
        else:
            if self.right_hand.fingers_up() % 2 == 1: raise Exception("Only available when even number of fingers")
            new_fingers = self.right_hand.fingers_up() // 2
            self.left_hand.update_hand(new_fingers)
            self.right_hand.update_hand(new_fingers)

    def checkLoss(self):
        return self.hands_up() == 0

    def make_move(self, opponent, move, p):
        if not move:
            raise Exception("No move found :(")
        m0 = move[0]
        m1 = move[1]
        if m0 != "l" and m0 != "r" and m0 != "s":
            raise Exception("Invalid first key!")
        if m1 != "l" and m1 != "r":
            raise Exception("Invalid second key!")
        if m0 == "l":
            if opponent.left_hand.fingers_up() == 0:
                raise Exception("Hand already dead!")
            if m1 == "l":
                if self.left_hand.fingers_up() == 0:
                    raise Exception("Cant hit with no fingers.")
                opponent.hit(self.left_hand.fingers_up(), True)
            if m1 == "r":
                if self.right_hand.fingers_up() == 0:
                    raise Exception("Cant hit with no fingers.")
                opponent.hit(self.right_hand.fingers_up(), True)
        if m0 == "r":
            if opponent.right_hand.fingers_up() == 0:
                raise Exception("Hand already dead!")
            if m1 == "l":
                if self.left_hand.fingers_up() == 0:
                    raise Exception("Cant hit with no fingers.")
                opponent.hit(self.left_hand.fingers_up(), False)
            if m1 == "r":
                if self.right_hand.fingers_up() == 0:
                    raise Exception("Cant hit with no fingers.")
                opponent.hit(self.right_hand.fingers_up(), False)
        if m0 == "s":
            if m1 == "l":
                self.split(True)
            if m1 == "r":
                self.split(False)
        m0 = move[0]
        m1 = move[1]
        if p:
            if m0 == "l":
                if m1 == "l":
                    print(f"{p} hits left hand with left hand!")
                if m1 == "r":
                    print(f"{p} hits left hand with right hand!")
            if m0 == "r":
                if m1 == "l":
                    print(f"{p} hits right hand with left hand!")
                if m1 == "r":
                    print(f"{p} hits right hand with right hand!")
            if m0 == "s":
                print(f"{p} splits!")

    def find_moves(self, opponent):
        lst = []
        if self.left_hand.fingers_up() > 0:
            if opponent.left_hand.fingers_up() > 0:
                lst.append("ll")
            if opponent.right_hand.fingers_up() > 0:
                lst.append("rl")
        if self.right_hand.fingers_up() > 0:
            if opponent.left_hand.fingers_up() > 0:
                lst.append("lr")
            if opponent.right_hand.fingers_up() > 0:
                lst.append("rr")
        if self.hands_up() == 1:
            if self.right_hand.fingers_up() > 0 and self.right_hand.fingers_up() % 2 == 0:
                lst.append("sr")
            if self.left_hand.fingers_up() > 0 and self.left_hand.fingers_up() % 2 == 0:
                lst.append("sl")
        return lst

    def printState(self):
        s = ""
        for finger in self.left_hand.fingers:
            if finger:
                s += "|"
            else:
                s += "_"
        s += "   "
        for finger in self.right_hand.fingers:
            if finger:
                s += "|"
            else:
                s += "_"
        return s

    def score(self, opponent, sense):
        if opponent.checkLoss(): return -1e99
        if self.checkLoss(): return 1e99
        AI_total = self.left_hand.fingers_up() + self.right_hand.fingers_up()
        opp_total = opponent.left_hand.fingers_up() + opponent.right_hand.fingers_up()
        return (AI_total-opp_total) * sense