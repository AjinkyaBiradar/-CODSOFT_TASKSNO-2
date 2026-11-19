"""
game.py
Core game logic and board state management for Tic-Tac-Toe.
"""

from typing import List, Optional, Tuple

EMPTY = ' '
PLAYER_X = 'X'
PLAYER_O = 'O'

WINNING_COMBINATIONS: Tuple[Tuple[int, int, int], ...] = (
    (0, 1, 2),  # Row 1
    (3, 4, 5),  # Row 2
    (6, 7, 8),  # Row 3
    (0, 3, 6),  # Column 1
    (1, 4, 7),  # Column 2
    (2, 5, 8),  # Column 3
    (0, 4, 8),  # Diagonal 1
    (2, 4, 6),  # Diagonal 2
)


class TicTacToe:
    """Manages the 3x3 Tic-Tac-Toe board, player turns, and win/draw evaluation."""

    def __init__(self, starting_player: str = PLAYER_X) -> None:
        self.board: List[str] = [EMPTY] * 9
        self.current_player: str = starting_player
        self.winner: Optional[str] = None
        self.winning_line: Optional[Tuple[int, int, int]] = None
        self.game_over: bool = False

    def reset(self, starting_player: str = PLAYER_X) -> None:
        """Reset the board to initial empty state."""
        self.board = [EMPTY] * 9
        self.current_player = starting_player
        self.winner = None
        self.winning_line = None
        self.game_over = False

    def available_moves(self) -> List[int]:
        """Return list of zero-indexed cell indices available for a move."""
        return [i for i, cell in enumerate(self.board) if cell == EMPTY]

    def make_move(self, index: int, player: Optional[str] = None) -> bool:
        """
        Place a player's mark at index.
        Updates board state, winner, winning line, and current player.
        Returns True if the move was valid and executed, False otherwise.
        """
        if self.game_over:
            return False
        if not (0 <= index <= 8):
            return False
        if self.board[index] != EMPTY:
            return False

        active_player = player if player is not None else self.current_player
        self.board[index] = active_player

        # Check win condition
        winner, line = self.check_winner()
        if winner is not None:
            self.winner = winner
            self.winning_line = line
            self.game_over = True
        elif self.is_full():
            self.winner = None
            self.winning_line = None
            self.game_over = True
        else:
            self.current_player = PLAYER_O if active_player == PLAYER_X else PLAYER_X

        return True

    def undo_move(self, index: int, previous_player: Optional[str] = None) -> None:
        """Undo a move at index. Useful for search backtracking."""
        if 0 <= index <= 8:
            self.board[index] = EMPTY
            self.winner = None
            self.winning_line = None
            self.game_over = False
            if previous_player is not None:
                self.current_player = previous_player

    def check_winner(self) -> Tuple[Optional[str], Optional[Tuple[int, int, int]]]:
        """Check if any player has won. Returns (winner, winning_line) or (None, None)."""
        for combo in WINNING_COMBINATIONS:
            a, b, c = combo
            if self.board[a] != EMPTY and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a], combo
        return None, None

    def is_full(self) -> bool:
        """Return True if no empty spaces remain on board."""
        return EMPTY not in self.board

    def is_terminal(self) -> bool:
        """Return True if game is over (win or draw)."""
        winner, _ = self.check_winner()
        return winner is not None or self.is_full()

    def clone(self) -> "TicTacToe":
        """Return a deep copy of the current game state."""
        new_game = TicTacToe(starting_player=self.current_player)
        new_game.board = list(self.board)
        new_game.winner = self.winner
        new_game.winning_line = self.winning_line
        new_game.game_over = self.game_over
        return new_game

    def __repr__(self) -> str:
        rows = [
            " | ".join(self.board[i : i + 3])
            for i in range(0, 9, 3)
        ]
        return "\n---------\n".join(rows)
