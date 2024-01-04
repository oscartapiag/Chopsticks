class Hand:
    def __init__(self):
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
    def __init__(self):
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
        if left:
            if self.hands_up() == 2: raise Exception("Only available when having one hand")
            if self.left_hand.fingers_up() % 2 == 1: raise Exception("Only available when even number of fingers")
            new_fingers = self.left_hand.fingers_up() // 2
            self.left_hand.update_hand(new_fingers)
            self.right_hand.update_hand(new_fingers)
        else:
            if self.hands_up() == 2: raise Exception("Only available when having one hand")
            if self.right_hand.fingers_up() % 2 == 1: raise Exception("Only available when even number of fingers")
            new_fingers = self.right_hand.fingers_up() // 2
            self.left_hand.update_hand(new_fingers)
            self.right_hand.update_hand(new_fingers)

    def checkLoss(self):
        return self.hands_up() == 0

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