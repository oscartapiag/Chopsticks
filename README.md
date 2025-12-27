# Chopsticks Game

A Python implementation of the classic hand game **Chopsticks**, featuring a graphical user interface (GUI) and an unbeatable AI opponent using the Minimax algorithm.

Now with website to play online: https://web-production-7e4d6.up.railway.app/

## Features

- **Two Modes**: Play via a modern GUI or a classic Command Line Interface (CLI).
- **Smart AI**: Challenge an AI that uses the Minimax algorithm with Alpha-Beta pruning to calculate optimal moves.
- **Game Logic**: Full implementation of standard Chopsticks rules, including splitting and transfers.

## Requirements

- Python 3.x
- Tkinter (usually included with standard Python installations)

## How to Run

### Graphical Interface
To play the game with the visual interface:
```bash
python gui.py
```

### Command Line Interface
To play the text-based version in your terminal:
```bash
python main.py
```

## Game Rules

1. **Setup**: Each player starts with two hands, each having 1 finger raised.
2. **Objective**: The goal is to make both of the opponent's hands go to 0 (dead).
3. **Turn Actions**:
   - **Hit**: Tap one of your live hands against an opponent's live hand. The opponent's hand count increases by your hand's count (modulo 5). If a hand reaches 5 (or 0), it is considered "dead".
   - **Split**: If you have two hands but one is dead (0 fingers), or if the game rules allow redistribution, you can split your fingers.
     - *Example*: If you have `[4, 0]`, you can split to `[2, 2]`.

## Project Structure

- `stick.py`: Core game logic (Hand and Player classes).
- `AI.py`: AI logic using Minimax.
- `gui.py`: Graphical User Interface using Tkinter.
- `game.py`: Game controller bridging the UI and logic.
