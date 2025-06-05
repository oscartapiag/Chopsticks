import tkinter as tk
from tkinter import ttk
from game import Game

# ─── COLOURS ───────────────────────────────────────────────────────────────
DARK_BG  = "#2b2b2b"
LIGHT_FG = "#ffffff"

BTN_BG        = "#3d3d3d"
BTN_BG_ACTIVE = "#555555"

# ─── ONE “FINGER” RECTANGLE ────────────────────────────────────────────────
RECT_W, RECT_H = 20, 10
GAP            = 4


def draw_fingers(canvas: tk.Canvas, n: int) -> None:
    """Draw n (0–4) vertical rectangles, bottom-aligned inside the canvas."""
    canvas.delete("all")
    total_h = 4 * RECT_H + 3 * GAP
    x0 = (canvas.winfo_width()  - RECT_W) // 2
    y0 = (canvas.winfo_height() - total_h) // 2
    for i in range(n):  # draw bottom-up
        y = y0 + total_h - (i + 1) * (RECT_H + GAP) + GAP
        canvas.create_rectangle(
            x0, y, x0 + RECT_W, y + RECT_H,
            fill=LIGHT_FG, outline=LIGHT_FG
        )


class ChopsticksGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Chopsticks")

        # — global dark-mode defaults —
        root.configure(bg=DARK_BG)
        for opt, val in (
            ("*background", DARK_BG),
            ("*foreground", LIGHT_FG),
            ("*insertBackground", LIGHT_FG),
        ):
            root.option_add(opt, val)

        # — ttk button style —
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure(
            "Move.TButton",
            foreground=LIGHT_FG,
            background=BTN_BG,
            borderwidth=0,
            padding=6,
        )
        style.map(
            "Move.TButton",
            foreground=[("active", LIGHT_FG)],
            background=[("active", BTN_BG_ACTIVE)],
        )

        # create initial game state
        self.game = Game(vs_ai=True, depth=5)

        # ─ GRID LAYOUT (no overlaps) ────────────────────────────────────
        root.columnconfigure(0, weight=1)  # single stretchable column

        # status label (row 0)
        self.status = tk.Label(root, font=("Helvetica", 14))
        self.status.grid(row=0, column=0, pady=(6, 2), sticky="n")

        # two fixed-height rows for hands: human (row 1) and AI (row 2)
        self._hand_row(row=1, is_human=True)
        self._hand_row(row=2, is_human=False)

        # move-button strip (row 3)
        self.btn_frame = tk.Frame(root, bg=DARK_BG)
        self.btn_frame.grid(row=3, column=0, pady=8)

        # allow only the log row (row 4) to absorb extra vertical space
        root.rowconfigure(4, weight=1)

        # log box (row 4)
        self.log = tk.Text(
            root,
            height=7,
            width=46,
            state="disabled",
            bg="#444444",
            fg=LIGHT_FG,
            insertbackground=LIGHT_FG,
        )
        self.log.grid(
            row=4, column=0, pady=(0, 4), padx=4, sticky="nsew"
        )

        # “Play Again” button (row 5)
        self.play_again_btn = ttk.Button(
            root,
            text="Play Again",
            style="Move.TButton",
            command=self.play_again
        )
        self.play_again_btn.grid(row=5, column=0, pady=(0, 8))

        # build the initial UI state
        self.refresh()
        root.mainloop()

    # ────────────────────────────────────────────────────────────────────
    def _hand_row(self, row: int, *, is_human: bool):
        """
        Build a single row (60 px tall) containing two canvases side-by-side.
        is_human=True → top row; False → AI row.
        """
        frame = tk.Frame(self.root, bg=DARK_BG, height=60)
        frame.grid(row=row, column=0, pady=4, sticky="n")
        frame.grid_propagate(False)  # freeze at 60 px

        canv_l = tk.Canvas(
            frame, width=60, height=60,
            bg=DARK_BG, highlightthickness=0
        )
        canv_r = tk.Canvas(
            frame, width=60, height=60,
            bg=DARK_BG, highlightthickness=0
        )
        canv_l.pack(side="left", padx=20)
        canv_r.pack(side="left", padx=20)

        # prevent the canvases from growing larger than 60×60
        canv_l.pack_propagate(False)
        canv_r.pack_propagate(False)

        if is_human:
            self.canvas_you_L, self.canvas_you_R = canv_l, canv_r
        else:
            self.canvas_ai_L, self.canvas_ai_R = canv_l, canv_r

    # ────────────────────────────────────────────────────────────────────
    def refresh(self) -> None:
        """Redraw all bones of the UI for the current game state."""
        # draw finger-count rectangles
        draw_fingers(self.canvas_you_L, self.game.left(0))
        draw_fingers(self.canvas_you_R, self.game.right(0))
        draw_fingers(self.canvas_ai_L,  self.game.left(1))
        draw_fingers(self.canvas_ai_R,  self.game.right(1))

        # update status label
        self.status["text"] = (
            "Your turn" if self.game.turn == 0 else "AI thinking…"
        )

        # (re)build the move buttons for the human turn
        for w in self.btn_frame.winfo_children():
            w.destroy()

        if self.game.turn == 0:
            for mv in dict.fromkeys(self.game.legal_moves()):
                lbl = "Split" if mv.lower().startswith("s") else mv.upper()
                # capture mv in a default arg so each button has its own command
                ttk.Button(
                    self.btn_frame,
                    text=lbl,
                    style="Move.TButton",
                    command=lambda m=mv: self.play_human(m)
                ).pack(side="left", padx=3)

    # ────────────────────────────────────────────────────────────────────
    def play_human(self, move: str) -> None:
        """Called when the human clicks a move-button."""
        self.log_line(f"You → {move}")
        self.game.apply_move(move)
        self.game.next_turn()
        if self.check_end():
            return
        self.refresh()
        # let the UI update before the AI thinks
        self.root.after(100, self.play_ai)

    def play_ai(self) -> None:
        """Invoke the AI’s move and update the UI."""
        mv = self.game.ai_move()
        self.log_line(f"AI → {mv}")
        self.game.apply_move(mv)
        self.game.next_turn()
        if self.check_end():
            return
        self.refresh()

    # ────────────────────────────────────────────────────────────────────
    def log_line(self, txt: str) -> None:
        """Append a line of text to the log box."""
        self.log.config(state="normal")
        self.log.insert("end", txt + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def check_end(self) -> bool:
        """
        Check if someone has won. If so, disable move buttons
        and leave a message. Return True if the game is over.
        """
        winner = self.game.winner()
        if winner is not None:
            self.status["text"] = (
                "You win! 🎉" if winner == 0 else "AI wins 😢"
            )
            for b in self.btn_frame.winfo_children():
                b.config(state="disabled")
            return True
        return False

    # ────────────────────────────────────────────────────────────────────
    def play_again(self) -> None:
        """
        Reset the game to a fresh state:
        • new backend Game()
        • clear the log
        • rebuild buttons & hands
        """
        # 1) Recreate game instance
        self.game = Game(vs_ai=True, depth=5)

        # 2) Clear the log box
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

        # 3) Re-enable move buttons (if they were disabled at game-end)
        for b in self.btn_frame.winfo_children():
            b.config(state="normal")

        # 4) Refresh the entire UI
        self.refresh()


# ── run directly ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    ChopsticksGUI(tk.Tk())
