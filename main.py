from stick import Player
from AI import AI

def playGame(Ai, difficulty):
    if Ai:
        human = Player()
        ai = AI(int(difficulty))
        turn = 0
        while True:

            if turn % 2 == 0:
                print("Player Turn")
                print(f"Player: {human.printState()}")
                print(f"AI: {ai.printState()}")
                inp1 = input("l to hit left hand, r to hit right hand, s to split!")
                inp2 = input("l to hit with your left, r to hit with your right or what hand to split!")
                move = inp1 + inp2
                try:
                    human.make_move(ai, move, "Player")
                except Exception:
                    print("Invalid move, please try again!")
                    continue
                if ai.checkLoss():
                    print("Player has won!!!")
                    break
            else:
                print("AI Turn")
                print(f"Player: {human.printState()}")
                print(f"AI: {ai.printState()}")
                move = ai.find_move(human)
                ai.make_move(human, move, "AI")
                if human.checkLoss():
                    print("AI has defeated you! :(")
                    break
            turn += 1
    else:
        P1 = Player()
        P2 = Player()
        turn = 0
        while True:
            if turn % 2 == 0:
                print("Player 1 Turn")
                print(f"Player 1: {P1.printState()}")
                print(f"Player 2: {P2.printState()}")
                inp1 = input("l to hit left hand, r to hit right hand, s to split!")
                inp2 = input("l to hit with your left, r to hit with your right or what hand to split!")
                move = inp1 + inp2
                try:
                    P1.make_move(P2, move, "Player 1")
                except Exception:
                    print("Invalid move, please try again!")
                    continue
                if P2.checkLoss():
                    print("Player 1 has won!!!")
                    break
            else:
                print("Player 2 Turn")
                print(f"Player "f"1: {P1.printState()}")
                print(f"Player 2: {P2.printState()}")
                inp1 = input("l to hit left hand, r to hit right hand, s to split!")
                inp2 = input("l to hit with your left, r to hit with your right or what hand to split!")
                move = inp1 + inp2
                try:
                    P2.make_move(P1, move, "Player 2")
                except Exception:
                    print("Invalid move, please try again!")
                    continue
                if P1.checkLoss():
                    print("Player 2 has won!!!")
                    break
            turn += 1

def main():
    print("AI? y/n")
    AI = input("")
    if AI == "y":
        b = True
        difficulty = input("Select difficulty, 1 | 2 | 3 | 4")
    else:
        difficulty = None
        b = False
    playGame(b, difficulty)

if __name__ == '__main__':
    main()



