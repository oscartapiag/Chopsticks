
import time
from game import Game
from AI import AI
from stick import Player, Hand

def benchmark(depth, complexity="start", runs=1):
    print(f"Benchmarking Depth {depth} ({complexity})...")
    ai = AI(depth)
    human = Player()
    
    if complexity == "complex":
        # Force a complex state
        # AI: 4, 3
        # Human: 2, 4
        # Lots of splits and attacks possible
        ai.left_hand.update_hand(4)
        ai.right_hand.update_hand(3)
        human.left_hand.update_hand(2)
        human.right_hand.update_hand(4)
    
    start = time.time()
    for _ in range(runs):
        ai.find_move(human)
    end = time.time()
    
    avg = (end - start) / runs
    print(f"Depth {depth} ({complexity}): {avg:.4f} seconds per move (avg of {runs} runs)")
    return avg

if __name__ == "__main__":
    benchmark(7, "complex", runs=3)
    benchmark(9, "complex", runs=3)
    benchmark(10, "complex", runs=3)
    benchmark(11, "complex", runs=1)
