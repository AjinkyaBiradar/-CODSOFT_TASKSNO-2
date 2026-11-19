"""
gui.py
Modern Tkinter Graphical User Interface for the Unbeatable Tic-Tac-Toe Game.
Features:
- Responsive 3x3 interactive board with winning line highlights.
- Human symbol choice (X or O) and starting player choice (Human or AI).
- Difficulty selector: Easy, Medium, Hard.
- Minimax vs Alpha-Beta Pruning real-time search node comparison panel.
- Score tracker (Human, AI, Ties) and Restart / Reset controls.
- Asynchronous AI calculation using threading to ensure 60fps smooth UI.
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional

from ai import (
    AIMoveResult,
    DIFFICULTY_EASY,
    DIFFICULTY_MEDIUM,
    DIFFICULTY_HARD,
    compute_ai_move,
)
from game import (
    EMPTY,
    PLAYER_O,
    PLAYER_X,
    TicTacToe,
)

# Color Scheme (Modern Sleek Dark Palette)
BG_DARK = "#181825"
CARD_BG = "#1e1e2e"
SURFACE_BG = "#313244"
TEXT_COLOR = "#cdd6f4"
TEXT_MUTED = "#a6adc8"
ACCENT_BLUE = "#89b4fa"
COLOR_X = "#38bdf8"        # Sky Blue for X
COLOR_O = "#f43f5e"        # Vibrant Rose/Coral for O
COLOR_WIN = "#10b981"      # Emerald green for winning cells
COLOR_WIN_TEXT = "#ffffff"
BTN_HOVER_BG = "#45475a"
BORDER_COLOR = "#45475a"


class TicTacToeGUI:
    """Tkinter GUI for the Unbeatable Tic-Tac-Toe AI."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Unbeatable Tic-Tac-Toe • Minimax vs Alpha-Beta")
        self.root.geometry("820x760")
        self.root.minsize(760, 720)
        self.root.configure(bg=BG_DARK)

        # Game state variables
        self.human_symbol_var = tk.StringVar(value=PLAYER_X)
        self.first_turn_var = tk.StringVar(value="Human")
        self.difficulty_var = tk.StringVar(value=DIFFICULTY_HARD)

        # Score counters
        self.scores: Dict[str, int] = {"Human": 0, "AI": 0, "Ties": 0}

        # Initialize Game Engine
        self.game = TicTacToe(starting_player=PLAYER_X)
        self.ai_player: str = PLAYER_O
        self.human_player: str = PLAYER_X
        self.is_ai_computing: bool = False

        # GUI elements tracking
        self.board_buttons: List[tk.Button] = []

        self._configure_styles()
        self._build_ui()
        self.restart_game(reset_board_only=True)

    def _configure_styles(self) -> None:
        """Configure ttk styles."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=BG_DARK, foreground=TEXT_COLOR)
        style.configure("TFrame", background=BG_DARK)
        style.configure("Card.TFrame", background=CARD_BG, relief="flat")
        style.configure("Surface.TFrame", background=SURFACE_BG, relief="flat")
        style.configure(
            "Header.TLabel",
            background=BG_DARK,
            foreground="#f5e0dc",
            font=("Segoe UI", 18, "bold"),
        )
        style.configure(
            "SubHeader.TLabel",
            background=CARD_BG,
            foreground=TEXT_MUTED,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Score.TLabel",
            background=CARD_BG,
            foreground=TEXT_COLOR,
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "ScoreVal.TLabel",
            background=CARD_BG,
            foreground=ACCENT_BLUE,
            font=("Segoe UI", 16, "bold"),
        )
        style.configure(
            "StatKey.TLabel",
            background=CARD_BG,
            foreground=TEXT_MUTED,
            font=("Segoe UI", 9),
        )
        style.configure(
            "StatVal.TLabel",
            background=CARD_BG,
            foreground="#a6e3a1",
            font=("Consolas", 10, "bold"),
        )

    def _build_ui(self) -> None:
        """Assemble all UI containers."""
        # Top Header
        header_frame = tk.Frame(self.root, bg=BG_DARK, pady=10)
        header_frame.pack(fill=tk.X, padx=20)

        title_lbl = tk.Label(
            header_frame,
            text="Unbeatable Tic-Tac-Toe AI",
            font=("Segoe UI", 20, "bold"),
            bg=BG_DARK,
            fg="#cdd6f4",
        )
        title_lbl.pack()

        subtitle_lbl = tk.Label(
            header_frame,
            text="Powered by Minimax with Alpha-Beta Pruning • Mathematical Guarantee: Never Loses",
            font=("Segoe UI", 10),
            bg=BG_DARK,
            fg=TEXT_MUTED,
        )
        subtitle_lbl.pack(pady=2)

        # Main horizontal split: Left (Controls + Board), Right (Stats & Analysis)
        content_frame = tk.Frame(self.root, bg=BG_DARK)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        left_pane = tk.Frame(content_frame, bg=BG_DARK)
        left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right_pane = tk.Frame(content_frame, bg=BG_DARK, width=320)
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_pane.pack_propagate(False)

        # --- LEFT PANE ---
        # 1. Config Bar (Options)
        self._build_options_bar(left_pane)

        # 2. Status message banner
        self.status_var = tk.StringVar(value="Your Turn")
        self.status_banner = tk.Label(
            left_pane,
            textvariable=self.status_var,
            font=("Segoe UI", 13, "bold"),
            bg=CARD_BG,
            fg=ACCENT_BLUE,
            pady=8,
            relief="flat",
        )
        self.status_banner.pack(fill=tk.X, pady=(10, 10))

        # 3. 3x3 Board Grid
        self._build_board(left_pane)

        # 4. Action Buttons (Restart, Reset Score)
        action_frame = tk.Frame(left_pane, bg=BG_DARK, pady=10)
        action_frame.pack(fill=tk.X)

        self.btn_restart = tk.Button(
            action_frame,
            text="↻  Restart Match",
            command=self.restart_game,
            font=("Segoe UI", 11, "bold"),
            bg="#89b4fa",
            fg="#11111b",
            activebackground="#b4befe",
            activeforeground="#11111b",
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=6,
        )
        self.btn_restart.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))

        self.btn_reset_scores = tk.Button(
            action_frame,
            text="Reset Scores",
            command=self.reset_scores,
            font=("Segoe UI", 10),
            bg=SURFACE_BG,
            fg=TEXT_COLOR,
            activebackground=BTN_HOVER_BG,
            activeforeground=TEXT_COLOR,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
        )
        self.btn_reset_scores.pack(side=tk.RIGHT, padx=(6, 0))

        # --- RIGHT PANE ---
        # 1. Score Tracker Card
        self._build_score_card(right_pane)

        # 2. Minimax vs Alpha-Beta Comparison Card
        self._build_stats_card(right_pane)

    def _build_options_bar(self, parent: tk.Widget) -> None:
        """Create controls for Symbol, First Turn, and Difficulty."""
        opts_card = tk.LabelFrame(
            parent,
            text=" Match Settings ",
            font=("Segoe UI", 10, "bold"),
            bg=CARD_BG,
            fg=TEXT_MUTED,
            relief="flat",
            padx=12,
            pady=8,
        )
        opts_card.pack(fill=tk.X)

        # Row 1: Symbol Choice
        row1 = tk.Frame(opts_card, bg=CARD_BG)
        row1.pack(fill=tk.X, pady=3)

        tk.Label(row1, text="Play As:", font=("Segoe UI", 10, "bold"), bg=CARD_BG, fg=TEXT_COLOR, width=12, anchor="w").pack(side=tk.LEFT)
        for sym in [PLAYER_X, PLAYER_O]:
            rb = tk.Radiobutton(
                row1,
                text=f" {sym} ",
                value=sym,
                variable=self.human_symbol_var,
                command=self.on_settings_changed,
                bg=CARD_BG,
                fg=COLOR_X if sym == PLAYER_X else COLOR_O,
                selectcolor=SURFACE_BG,
                activebackground=CARD_BG,
                activeforeground=TEXT_COLOR,
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
            )
            rb.pack(side=tk.LEFT, padx=10)

        # Row 2: Turn Choice
        row2 = tk.Frame(opts_card, bg=CARD_BG)
        row2.pack(fill=tk.X, pady=3)

        tk.Label(row2, text="First Move:", font=("Segoe UI", 10, "bold"), bg=CARD_BG, fg=TEXT_COLOR, width=12, anchor="w").pack(side=tk.LEFT)
        for turn in ["Human", "AI"]:
            rb = tk.Radiobutton(
                row2,
                text=f" {turn} ",
                value=turn,
                variable=self.first_turn_var,
                command=self.on_settings_changed,
                bg=CARD_BG,
                fg=TEXT_COLOR,
                selectcolor=SURFACE_BG,
                activebackground=CARD_BG,
                activeforeground=TEXT_COLOR,
                font=("Segoe UI", 10),
                cursor="hand2",
            )
            rb.pack(side=tk.LEFT, padx=10)

        # Row 3: Difficulty Choice
        row3 = tk.Frame(opts_card, bg=CARD_BG)
        row3.pack(fill=tk.X, pady=3)

        tk.Label(row3, text="Difficulty:", font=("Segoe UI", 10, "bold"), bg=CARD_BG, fg=TEXT_COLOR, width=12, anchor="w").pack(side=tk.LEFT)
        for diff, col in [
            (DIFFICULTY_EASY, "#a6e3a1"),
            (DIFFICULTY_MEDIUM, "#f9e2af"),
            (DIFFICULTY_HARD, "#f38ba8"),
        ]:
            rb = tk.Radiobutton(
                row3,
                text=f" {diff} ",
                value=diff,
                variable=self.difficulty_var,
                bg=CARD_BG,
                fg=col,
                selectcolor=SURFACE_BG,
                activebackground=CARD_BG,
                activeforeground=col,
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
            )
            rb.pack(side=tk.LEFT, padx=6)

    def _build_board(self, parent: tk.Widget) -> None:
        """Create the 3x3 clickable grid."""
        board_container = tk.Frame(parent, bg=BORDER_COLOR, padx=3, pady=3)
        board_container.pack(expand=True, pady=5)

        self.board_buttons = []
        for i in range(9):
            r, c = divmod(i, 3)
            btn = tk.Button(
                board_container,
                text=" ",
                font=("Segoe UI", 28, "bold"),
                width=4,
                height=2,
                bg=CARD_BG,
                fg=TEXT_COLOR,
                activebackground=BTN_HOVER_BG,
                activeforeground=TEXT_COLOR,
                relief="flat",
                cursor="hand2",
                command=lambda idx=i: self.on_cell_clicked(idx),
            )
            btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
            self.board_buttons.append(btn)

    def _build_score_card(self, parent: tk.Widget) -> None:
        """Create the scoreboard widget."""
        score_frame = tk.LabelFrame(
            parent,
            text=" Scoreboard ",
            font=("Segoe UI", 10, "bold"),
            bg=CARD_BG,
            fg=TEXT_MUTED,
            relief="flat",
            padx=12,
            pady=10,
        )
        score_frame.pack(fill=tk.X, pady=(0, 10))

        cols = [
            ("Human", "lbl_score_human", COLOR_X),
            ("Ties", "lbl_score_ties", TEXT_MUTED),
            ("AI", "lbl_score_ai", COLOR_O),
        ]

        self.score_labels: Dict[str, tk.Label] = {}
        for idx, (title, key, color) in enumerate(cols):
            sub = tk.Frame(score_frame, bg=CARD_BG)
            sub.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

            lbl_t = tk.Label(sub, text=title, font=("Segoe UI", 9, "bold"), bg=CARD_BG, fg=TEXT_MUTED)
            lbl_t.pack()

            lbl_v = tk.Label(sub, text="0", font=("Segoe UI", 18, "bold"), bg=CARD_BG, fg=color)
            lbl_v.pack()
            self.score_labels[title] = lbl_v

    def _build_stats_card(self, parent: tk.Widget) -> None:
        """Create the Minimax vs Alpha-Beta live comparison metrics panel."""
        stats_frame = tk.LabelFrame(
            parent,
            text=" Search Tree Analysis ",
            font=("Segoe UI", 10, "bold"),
            bg=CARD_BG,
            fg=TEXT_MUTED,
            relief="flat",
            padx=12,
            pady=10,
        )
        stats_frame.pack(fill=tk.BOTH, expand=True)

        intro = tk.Label(
            stats_frame,
            text="Real-time node count benchmark\non every AI move:",
            font=("Segoe UI", 9),
            bg=CARD_BG,
            fg=TEXT_MUTED,
            justify=tk.LEFT,
        )
        intro.pack(anchor="w", pady=(0, 10))

        # Plain Minimax Metric
        f_plain = tk.Frame(stats_frame, bg=SURFACE_BG, padx=10, pady=8)
        f_plain.pack(fill=tk.X, pady=4)
        tk.Label(f_plain, text="Plain Minimax Nodes:", font=("Segoe UI", 9), bg=SURFACE_BG, fg=TEXT_COLOR).pack(anchor="w")
        self.lbl_plain_nodes = tk.Label(f_plain, text="--", font=("Consolas", 14, "bold"), bg=SURFACE_BG, fg="#fab387")
        self.lbl_plain_nodes.pack(anchor="w")
        self.lbl_plain_time = tk.Label(f_plain, text="Search time: --", font=("Segoe UI", 8), bg=SURFACE_BG, fg=TEXT_MUTED)
        self.lbl_plain_time.pack(anchor="w")

        # Alpha-Beta Metric
        f_ab = tk.Frame(stats_frame, bg=SURFACE_BG, padx=10, pady=8)
        f_ab.pack(fill=tk.X, pady=4)
        tk.Label(f_ab, text="Alpha-Beta Pruned Nodes:", font=("Segoe UI", 9), bg=SURFACE_BG, fg=TEXT_COLOR).pack(anchor="w")
        self.lbl_ab_nodes = tk.Label(f_ab, text="--", font=("Consolas", 14, "bold"), bg=SURFACE_BG, fg="#a6e3a1")
        self.lbl_ab_nodes.pack(anchor="w")
        self.lbl_ab_time = tk.Label(f_ab, text="Search time: --", font=("Segoe UI", 8), bg=SURFACE_BG, fg=TEXT_MUTED)
        self.lbl_ab_time.pack(anchor="w")

        # Efficiency Gain / Reduction
        f_eff = tk.Frame(stats_frame, bg=CARD_BG, padx=4, pady=8)
        f_eff.pack(fill=tk.X, pady=4)
        tk.Label(f_eff, text="Pruning Efficiency:", font=("Segoe UI", 9, "bold"), bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w")
        self.lbl_reduction = tk.Label(
            f_eff,
            text="Waiting for AI turn...",
            font=("Segoe UI", 11, "bold"),
            bg=CARD_BG,
            fg=ACCENT_BLUE,
            wraplength=270,
            justify=tk.LEFT,
        )
        self.lbl_reduction.pack(anchor="w", pady=2)

        # Algorithm Explanation
        tip_box = tk.Label(
            stats_frame,
            text=(
                "ℹ Alpha-Beta Pruning discards game branches that cannot alter the optimal outcome, "
                "evaluating up to 96% fewer nodes while guaranteeing the exact same unbeatable move."
            ),
            font=("Segoe UI", 8),
            bg=CARD_BG,
            fg=TEXT_MUTED,
            wraplength=270,
            justify=tk.LEFT,
        )
        tip_box.pack(side=tk.BOTTOM, fill=tk.X, pady=6)

    def on_settings_changed(self) -> None:
        """Triggered when Symbol or Turn radio buttons change."""
        self.restart_game(reset_board_only=True)

    def restart_game(self, reset_board_only: bool = False) -> None:
        """Reset board state according to current settings and kick off AI if AI starts."""
        if self.is_ai_computing:
            return  # Prevent restarting while calculation thread is active

        self.human_player = self.human_symbol_var.get()
        self.ai_player = PLAYER_O if self.human_player == PLAYER_X else PLAYER_X

        first_turn = self.first_turn_var.get()
        starting_symbol = self.human_player if first_turn == "Human" else self.ai_player

        self.game.reset(starting_player=starting_symbol)
        self._update_board_ui()

        # Reset button states
        for btn in self.board_buttons:
            btn.config(
                bg=CARD_BG,
                activebackground=BTN_HOVER_BG,
                state=tk.NORMAL,
                cursor="hand2",
            )

        if first_turn == "Human":
            self.status_var.set(f"Your Turn ({self.human_player})")
            self.status_banner.config(fg=COLOR_X if self.human_player == PLAYER_X else COLOR_O)
        else:
            self.status_var.set("AI is contemplating opening move...")
            self.status_banner.config(fg=ACCENT_BLUE)
            self._schedule_ai_move()

    def reset_scores(self) -> None:
        """Reset all score counters to zero."""
        self.scores = {"Human": 0, "AI": 0, "Ties": 0}
        self.score_labels["Human"].config(text="0")
        self.score_labels["AI"].config(text="0")
        self.score_labels["Ties"].config(text="0")

    def on_cell_clicked(self, index: int) -> None:
        """Handle human player clicking a grid cell."""
        if self.game.game_over or self.is_ai_computing:
            return
        if self.game.current_player != self.human_player:
            return
        if self.game.board[index] != EMPTY:
            return

        # Execute human move
        success = self.game.make_move(index, player=self.human_player)
        if not success:
            return

        self._update_board_ui()

        if self.game.game_over:
            self._handle_game_over()
        else:
            self.status_var.set("AI is thinking...")
            self.status_banner.config(fg=ACCENT_BLUE)
            self._schedule_ai_move()

    def _schedule_ai_move(self) -> None:
        """Run AI search in a background thread to keep Tkinter silky smooth."""
        self.is_ai_computing = True
        self._set_board_interactive(False)

        difficulty = self.difficulty_var.get()
        ai_symbol = self.ai_player
        game_clone = self.game.clone()

        def worker() -> None:
            result = compute_ai_move(game_clone, difficulty=difficulty, ai_player=ai_symbol)
            # Post back to Tkinter event loop
            self.root.after(0, self._apply_ai_move, result)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def _apply_ai_move(self, result: Optional[AIMoveResult]) -> None:
        """Callback on main thread to apply AI move and update metrics."""
        self.is_ai_computing = False
        self._set_board_interactive(True)

        if result is None or self.game.game_over:
            return

        # Update metrics panel
        self._update_metrics_panel(result)

        # Execute AI move on game board
        self.game.make_move(result.chosen_move, player=self.ai_player)
        self._update_board_ui()

        if self.game.game_over:
            self._handle_game_over()
        else:
            self.status_var.set(f"Your Turn ({self.human_player})")
            self.status_banner.config(fg=COLOR_X if self.human_player == PLAYER_X else COLOR_O)

    def _set_board_interactive(self, enabled: bool) -> None:
        """Enable or disable board clicks while AI computes."""
        for i, btn in enumerate(self.board_buttons):
            if self.game.board[i] == EMPTY:
                btn.config(cursor="hand2" if enabled else "watch")

    def _update_board_ui(self) -> None:
        """Sync button text and colors with current board state."""
        for i, cell in enumerate(self.game.board):
            btn = self.board_buttons[i]
            btn.config(text=cell)
            if cell == PLAYER_X:
                btn.config(fg=COLOR_X)
            elif cell == PLAYER_O:
                btn.config(fg=COLOR_O)
            else:
                btn.config(fg=TEXT_COLOR)

    def _update_metrics_panel(self, result: AIMoveResult) -> None:
        """Display Plain Minimax vs Alpha-Beta node counts and reduction."""
        self.lbl_plain_nodes.config(text=f"{result.plain_nodes:,}")
        self.lbl_plain_time.config(text=f"Search time: {result.plain_duration_ms:.1f} ms")

        self.lbl_ab_nodes.config(text=f"{result.ab_nodes:,}")
        self.lbl_ab_time.config(text=f"Search time: {result.ab_duration_ms:.1f} ms")

        if result.plain_nodes > 0:
            diff = result.plain_nodes - result.ab_nodes
            self.lbl_reduction.config(
                text=f"✂ {result.reduction_percentage:.1f}% Reduction\n({diff:,} redundant nodes pruned)",
                fg="#a6e3a1" if result.reduction_percentage > 50 else ACCENT_BLUE,
            )
        else:
            self.lbl_reduction.config(text="Terminal state reached.", fg=TEXT_MUTED)

    def _handle_game_over(self) -> None:
        """Highlight winning line, update score tracker, and show final message."""
        winner, winning_line = self.game.check_winner()

        if winner is not None and winning_line is not None:
            # Highlight winning cells with vibrant emerald
            for idx in winning_line:
                self.board_buttons[idx].config(
                    bg=COLOR_WIN,
                    fg=COLOR_WIN_TEXT,
                    activebackground=COLOR_WIN,
                    activeforeground=COLOR_WIN_TEXT,
                )

            if winner == self.human_player:
                self.scores["Human"] += 1
                self.score_labels["Human"].config(text=str(self.scores["Human"]))
                self.status_var.set("🎉 Congratulations! You Won!")
                self.status_banner.config(fg="#a6e3a1")
            else:
                self.scores["AI"] += 1
                self.score_labels["AI"].config(text=str(self.scores["AI"]))
                self.status_var.set("🤖 AI Wins! Unbeatable algorithm proved.")
                self.status_banner.config(fg=COLOR_O)
        else:
            # Draw
            self.scores["Ties"] += 1
            self.score_labels["Ties"].config(text=str(self.scores["Ties"]))
            self.status_var.set("🤝 Game Tied! Perfectly played by both.")
            self.status_banner.config(fg="#f9e2af")

        # Disable all board cells
        for btn in self.board_buttons:
            btn.config(cursor="arrow")
