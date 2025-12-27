import tkinter as tk
from tkinter import font
from game import Game

# ─── THEME CONFIGURATION ───────────────────────────────────────────────────
COLORS = {
    "bg":      "#1E1E2E",  # Dark background
    "fg":      "#CDD6F4",  # Light text
    "human":   "#89B4FA",  # Blue for player
    "ai":      "#F38BA8",  # Red for AI
    "finger":  "#F9E2AF",  # Yellow/Peach for active fingers
    "empty":   "#313244",  # Dark grey for empty slots
    "select":  "#A6E3A1",  # Green highlight
    "btn_bg":  "#45475A",
    "btn_fg":  "#FFFFFF"
}

class ChopsticksGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Chopsticks Pro")
        self.root.geometry("600x800")
        self.root.configure(bg=COLORS["bg"])

        # Game State
        self.game = Game(vs_ai=True, depth=5)
        self.selected_hand = None  # None or 'l' or 'r' (Player's hand)
        self.game_over = False

        # Fonts
        self.font_main = font.Font(family="Helvetica", size=16, weight="bold")
        self.font_sub = font.Font(family="Helvetica", size=12)

        # Layout
        self._setup_layout()
        self.refresh()

    def _setup_layout(self):
        # 1. Header / Status
        self.header_frame = tk.Frame(self.root, bg=COLORS["bg"])
        self.header_frame.pack(pady=20, fill="x")
        
        self.status_lbl = tk.Label(
            self.header_frame, text="Your Turn", 
            font=("Helvetica", 24, "bold"), bg=COLORS["bg"], fg=COLORS["human"]
        )
        self.status_lbl.pack()

        self.sub_status_lbl = tk.Label(
            self.header_frame, text="Select a hand to move",
            font=self.font_sub, bg=COLORS["bg"], fg=COLORS["fg"]
        )
        self.sub_status_lbl.pack(pady=5)

        # 2. Game Area (Canvas)
        self.game_frame = tk.Frame(self.root, bg=COLORS["bg"])
        self.game_frame.pack(expand=True, fill="both", padx=20)

        # AI Hands (Top)
        self.ai_frame = tk.Frame(self.game_frame, bg=COLORS["bg"])
        self.ai_frame.pack(pady=20)
        
        tk.Label(self.ai_frame, text="AI (Opponent)", font=self.font_main, bg=COLORS["bg"], fg=COLORS["ai"]).pack(pady=(0, 10))
        
        self.ai_hands_container = tk.Frame(self.ai_frame, bg=COLORS["bg"])
        self.ai_hands_container.pack()
        
        self.cv_ai_l = self._create_hand_canvas(self.ai_hands_container, "ai_l")
        self.cv_ai_r = self._create_hand_canvas(self.ai_hands_container, "ai_r")

        # Spacer / VS
        tk.Label(self.game_frame, text="VS", font=("Helvetica", 14, "italic"), bg=COLORS["bg"], fg="#585B70").pack(pady=10)

        # Human Hands (Bottom)
        self.human_frame = tk.Frame(self.game_frame, bg=COLORS["bg"])
        self.human_frame.pack(pady=20)
        
        tk.Label(self.human_frame, text="YOU", font=self.font_main, bg=COLORS["bg"], fg=COLORS["human"]).pack(pady=(0, 10))
        
        self.human_hands_container = tk.Frame(self.human_frame, bg=COLORS["bg"])
        self.human_hands_container.pack()

        self.cv_human_l = self._create_hand_canvas(self.human_hands_container, "human_l")
        self.cv_human_r = self._create_hand_canvas(self.human_hands_container, "human_r")

        # 3. Controls / Log
        self.controls_frame = tk.Frame(self.root, bg=COLORS["bg"])
        self.controls_frame.pack(side="bottom", fill="x", pady=20, padx=20)

        self.log_text = tk.Text(self.controls_frame, height=5, bg="#181825", fg=COLORS["fg"], 
                                font=("Consolas", 10), relief="flat", state="disabled")
        self.log_text.pack(fill="x", pady=(0, 10))

        self.btn_reset = tk.Button(
            self.controls_frame, text="New Game", command=self.reset_game,
            bg=COLORS["select"], fg=COLORS["bg"], font=self.font_sub,
            highlightbackground=COLORS["select"],
            relief="flat", padx=20, pady=10, activebackground=COLORS["human"]
        )
        self.btn_reset.pack()

    def _create_hand_canvas(self, parent, tag):
        cv = tk.Canvas(parent, width=120, height=120, bg=COLORS["bg"], highlightthickness=0)
        cv.pack(side="left", padx=20)
        # Bind click
        cv.bind("<Button-1>", lambda e, t=tag: self.on_hand_click(t))
        return cv

    def draw_hand(self, canvas, fingers, is_human, is_selected):
        canvas.delete("all")
        w, h = 120, 120
        cx = w // 2

        # Orientation: Human hands at bottom pointing up, AI at top pointing down
        if is_human:
            cy = h - 35
            dy = -1
        else:
            cy = 35
            dy = 1

        # Colors
        base_color = COLORS["human"] if is_human else COLORS["ai"]
        palm_fill = COLORS["select"] if is_selected else base_color
        finger_fill = COLORS["finger"]

        # 1. Draw Fingers (behind palm)
        # Calculate offsets to center the fingers
        offsets = []
        if fingers == 1: offsets = [0]
        elif fingers == 2: offsets = [-12, 12]
        elif fingers == 3: offsets = [-20, 0, 20]
        elif fingers == 4: offsets = [-28, -10, 10, 28]

        for off in offsets:
            x = cx + off
            # Start inside the palm, extend out
            canvas.create_line(x, cy, x, cy + (dy * 50), 
                               width=14, fill=finger_fill, capstyle=tk.ROUND)
        
        # 2. Draw Palm (Circle on top)
        r = 30
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline=base_color, width=3, fill=palm_fill)

        # Text count
        canvas.create_text(cx, cy, text=str(fingers), fill=COLORS["bg"], font=("Helvetica", 16, "bold"))

    def refresh(self):
        # Get states
        h_l = self.game.left(0)
        h_r = self.game.right(0)
        a_l = self.game.left(1)
        a_r = self.game.right(1)

        # Draw
        self.draw_hand(self.cv_human_l, h_l, True, self.selected_hand == 'l')
        self.draw_hand(self.cv_human_r, h_r, True, self.selected_hand == 'r')
        self.draw_hand(self.cv_ai_l, a_l, False, False)
        self.draw_hand(self.cv_ai_r, a_r, False, False)

        # Status
        if self.game_over: return

        if self.game.turn == 0:
            self.status_lbl.config(text="Your Turn", fg=COLORS["human"])
            if self.selected_hand:
                self.sub_status_lbl.config(text="Select a target to attack or split")
            else:
                self.sub_status_lbl.config(text="Select your hand")
        else:
            self.status_lbl.config(text="AI Thinking...", fg=COLORS["ai"])
            self.sub_status_lbl.config(text="Please wait")

    def log(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"> {msg}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def on_hand_click(self, tag):
        if self.game.turn != 0 or self.game_over: return

        owner, side = tag.split('_') # owner="human"|"ai", side="l"|"r"
        print(f"[DEBUG] Clicked: {tag} | Current Selection: {self.selected_hand}")
        
        if self.selected_hand is None:
            if owner == "ai":
                self.log("Select your own hand first!")
                return
            fingers = self.game.left(0) if side == 'l' else self.game.right(0)
            if fingers == 0:
                self.log("Cannot select empty hand.")
                return
            self.selected_hand = side
            self.refresh()
        else:
            source = self.selected_hand
            target = side
            if owner == "human":
                if source == target:
                    print(f"[DEBUG] Deselecting {source}")
                    self.selected_hand = None # Deselect
                    self.refresh()
                else:
                    # Split: "s" + source
                    self.attempt_move("s" + source, f"Split {source.upper()} to {target.upper()}")
                    # Try Split
                    print(f"[DEBUG] Attempting Split {source}->{target}")
                    try:
                        self.game.apply_move("s" + source)
                        self.log(f"You: Split {source.upper()} to {target.upper()}")
                        self.selected_hand = None
                        self.game.next_turn()
                        self.refresh()
                        self.check_win()
                        if not self.game_over:
                            self.root.after(800, self.ai_turn)
                    except Exception as e:
                        print(f"[DEBUG] Split failed: {e}")
                        # If split failed (e.g. 2 hands alive), switch selection to the clicked hand if it has fingers
                        fingers = self.game.left(0) if target == 'l' else self.game.right(0)
                        if fingers > 0:
                            print(f"[DEBUG] Switching selection to {target}")
                            self.selected_hand = target
                        else:
                            self.log(f"Invalid move: {e}")
                        self.refresh()
            else:
                # Attack: source + target
                print(f"[DEBUG] Attempting Hit {source}->{target}")
                self.attempt_move(target + source, f"Hit {source.upper()} -> {target.upper()}")

    def attempt_move(self, move, desc):
        try:
            self.game.apply_move(move)
            self.log(f"You: {desc}")
            self.selected_hand = None
            self.game.next_turn()
            self.refresh()
            self.check_win()
            if not self.game_over:
                self.root.after(800, self.ai_turn)
        except Exception as e:
            print(f"[DEBUG] Move failed: {e}")
            self.log(f"Invalid move: {e}")
            self.selected_hand = None
            # Do not deselect on failure, allows user to retry easily
            self.refresh()

    def ai_turn(self):
        if self.game_over: return
        try:
            move = self.game.ai_move()
            self.game.apply_move(move)
            desc = f"Split {move[1].upper()}" if move[0] == 's' else f"Hit {move[0].upper()} -> {move[1].upper()}"
            self.log(f"AI: {desc}")
            self.game.next_turn()
            self.refresh()
            self.check_win()
        except Exception as e:
            self.log(f"AI Error: {e}")

    def check_win(self):
        w = self.game.winner()
        if w is not None:
            self.game_over = True
            if w == 0:
                self.status_lbl.config(text="YOU WIN! 🎉", fg=COLORS["select"])
                self.sub_status_lbl.config(text="Congratulations!")
            else:
                self.status_lbl.config(text="AI WINS 💀", fg=COLORS["ai"])
                self.sub_status_lbl.config(text="Better luck next time.")

    def reset_game(self):
        self.game = Game(vs_ai=True, depth=5)
        self.selected_hand = None
        self.game_over = False
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
        self.log("Game Started.")
        self.refresh()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChopsticksGUI(root)
    root.mainloop()
