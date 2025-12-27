# Project Documentation

## Architecture Overview

The project is organized into four main layers, separating concerns between logic, intelligence, control, and presentation:

1. **Core Logic (`stick.py`)**: Handles the fundamental rules of the game.
2. **Artificial Intelligence (`AI.py`)**: Implements the decision-making engine.
3. **Game Controller (`game.py`)**: Acts as a facade to manage game state for the UI.
4. **User Interface (`gui.py`, `main.py`)**: Handles user interaction.

---

## Module Details

### 1. Core Logic (`stick.py`)

#### `Hand` Class
Represents a single hand in the game.
- **Attributes**:
  - `count`: Integer representing the number of fingers up (0-4).
- **Methods**:
  - `update_hand(num)`: Sets the finger count, ensuring it is valid (0-5).
  - `hit_hand(num)`: Adds `num` to the current count modulo 5.
  - `fingers_up()`: Returns the current count.

#### `Player` Class
Represents a player with two hands.
- **Attributes**:
  - `left_hand`, `right_hand`: Instances of the `Hand` class.
- **Methods**:
  - `hit(num, left)`: Attacks a specific hand (left or right) with `num` fingers.
  - `split(left)`: Redistributes fingers between hands (e.g., 4/0 becomes 2/2).
  - `checkLoss()`: Returns `True` if both hands are 0.
  - `make_move(opponent, move, p)`: Executes a move string (e.g., "ll" for Left hits Left, "sr" for Split Right).
  - `find_moves(opponent)`: Generates a list of all legal moves in the current state.

### 2. Artificial Intelligence (`AI.py`)

#### `AI` Class (Inherits from `Player`)
- **Algorithm**: Minimax with Alpha-Beta Pruning.
- **Methods**:
  - `find_move(opponent)`: Calculates the best move to make against the given opponent.
  - `min_max(...)`: Recursive function that simulates game states to determine the score of a move.
  - `score(...)`: Heuristic function to evaluate a board state if the recursion depth limit is reached.

### 3. Game Controller (`game.py`)

#### `Game` Class
Facilitates communication between the UI and the Logic/AI.
- **Attributes**:
  - `human`: The human player object.
  - `ai`: The AI (or second human) player object.
  - `turn`: Integer (0 for Human, 1 for AI).
- **Methods**:
  - `legal_moves()`: Returns valid moves for the current player.
  - `apply_move(move)`: Applies a move string to the game state.
  - `ai_move()`: Triggers the AI to calculate its next move.
  - `winner()`: Checks if there is a winner (returns 0 for Human, 1 for AI, None otherwise).

### 4. User Interface

- **`gui.py`**: A Tkinter-based GUI. It visualizes the hands as circles with dots for fingers and allows interaction via clicking.
- **`main.py`**: A text-based entry point for playing in the terminal.