from stick import Player
from AI import AI

def playGame(Ai):
    if Ai:
        human = Player()
        ai = AI()
        turn = 0
        while True:
            if turn % 2 == 0:
                print("Player Turn")
                print(f"Player: {human.printState()}")
                print(f"AI: {ai.printState()}")
                inp1 = input("l to hit left hand, r to hit right hand, s to split!")
                inp2 = input("l to hit with your left, r to hit with your right or what hand to split!")
                if inp1 == "l":
                    if inp2 == "l":
                        ai.hit(human.left_hand.fingers_up(), True)
                    elif inp2 == "r":
                        ai.hit(human.right_hand.fingers_up(), True)
                    else:
                        raise Exception("Invalid Input!")
                elif inp1 == "r":
                    if inp2 == "l":
                        ai.hit(human.left_hand.fingers_up(), False)
                    elif inp2 == "r":
                        ai.hit(human.right_hand.fingers_up(), False)
                    else:
                        raise Exception("Invalid Input!")
                elif inp1 == "s":
                    if inp2 == "l":
                        human.split(True)
                    elif inp2 == "r":
                        human.split(False)
                    else:
                        raise Exception("Invalid Input!")
                if ai.checkLoss():
                    print("Player has won!!!")
                    break
            else:
                print("AI Turn")
                print(f"Player: {human.printState()}")
                print(f"AI: {ai.printState()}")
                move = ai.find_move(human)
                ai.make_move(human, move)
                m0 = move[0]
                m1 = move[1]
                if m0 == "l":
                    if m1 == "l":
                        print("AI hits left hand with left hand!")
                    if m1 == "r":
                        print("AI hits left hand with right hand!")
                if m0 == "r":
                    if m1 == "l":
                        print("AI hits right hand with left hand!")
                    if m1 == "r":
                        print("AI hits right hand with right hand!")
                if m0 == "s":
                    print("AI splits!")
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
                if inp1 == "l":
                    if inp2 == "l":
                        P2.hit(P1.left_hand.fingers_up(), True)
                    elif inp2 == "r":
                        P2.hit(P1.right_hand.fingers_up(), True)
                    else:
                        raise Exception("Invalid Input!")
                elif inp1 == "r":
                    if inp2 == "l":
                        P2.hit(P1.left_hand.fingers_up(), False)
                    elif inp2 == "r":
                        P2.hit(P1.right_hand.fingers_up(), False)
                    else:
                        raise Exception("Invalid Input!")
                elif inp1 == "s":
                    if inp2 == "l":
                        P1.split(True)
                    elif inp2 == "r":
                        P1.split(False)
                    else:
                        raise Exception("Invalid Input!")
                if P2.checkLoss():
                    print("Player 1 has won!!!")
                    break
            else:
                print("Player 2 Turn")
                print(f"Player 1: {P1.printState()}")
                print(f"Player 2: {P2.printState()}")
                inp1 = input("l to hit left hand, r to hit right hand, s to split!")
                inp2 = input("l to hit with your left, r to hit with your right or what hand to split!")
                if inp1 == "l":
                    if inp2 == "l":
                        P1.hit(P2.left_hand.fingers_up(), True)
                    elif inp2 == "r":
                        P1.hit(P2.right_hand.fingers_up(), True)
                    else:
                        raise Exception("Invalid Input!")
                elif inp1 == "r":
                    if inp2 == "l":
                        P1.hit(P2.left_hand.fingers_up(), False)
                    elif inp2 == "r":
                        P1.hit(P2.right_hand.fingers_up(), False)
                    else:
                        raise Exception("Invalid Input!")
                elif inp1 == "s":
                    if inp2 == "l":
                        P2.split(True)
                    elif inp2 == "r":
                        P2.split(False)
                    else:
                        raise Exception("Invalid Input!")
                if P1.checkLoss():
                    print("Player 2 has won!!!")
                    break
            turn += 1

def main():
    print("AI? y/n")
    AI = input("")
    if AI == "y":
        b = True
    else:
        b = False
    playGame(b)

if __name__ == '__main__':
    main()



