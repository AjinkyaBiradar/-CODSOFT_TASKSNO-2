"""
main.py
Application entry point for the Unbeatable Tic-Tac-Toe Game.
"""

import tkinter as tk
from gui import TicTacToeGUI


def main() -> None:
    """Initialize Tk root window and launch TicTacToe GUI."""
    root = tk.Tk()
    app = TicTacToeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
