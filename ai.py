"""
ai.py
Artificial Intelligence engine for Tic-Tac-Toe.
Implements Plain Minimax and Minimax with Alpha-Beta Pruning,
tracks explored search nodes, and supports Easy, Medium, and Hard difficulty levels.
"""

import math
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from game import EMPTY, PLAYER_O, PLAYER_X, TicTacToe, WINNING_COMBINATIONS

DIFFICULTY_EASY = "Easy"
DIFFICULTY_MEDIUM = "Medium"
DIFFICULTY_HARD = "Hard"


@dataclass
class AIMoveResult:
    """Contains AI move decision, performance metrics, and node counts."""
    chosen_move: int
    difficulty: str
    plain_nodes: int
    ab_nodes: int
    ab_best_move: int
    reduction_percentage: float
    ab_duration_ms: float
    plain_duration_ms: float
    eval_score: int


def _quick_check_winner(board: List[str]) -> Optional[str]:
    """Optimized winner check for search loops."""
    for a, b, c in WINNING_COMBINATIONS:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a]
    return None


def plain_minimax(
    board: List[str],
    depth: int,
    is_maximizing: bool,
    ai_player: str,
    human_player: str,
    counter: Dict[str, int],
) -> Tuple[int, Optional[int]]:
    """
    Plain recursive Minimax algorithm exploring all possible game states without pruning.
    Returns (score, best_move).
    """
    counter["nodes"] += 1

    winner = _quick_check_winner(board)
    if winner == ai_player:
        return 10 - depth, None
    if winner == human_player:
        return depth - 10, None

    available = [i for i, cell in enumerate(board) if cell == EMPTY]
    if not available:
        return 0, None  # Draw

    if is_maximizing:
        best_score = -math.inf
        best_move: Optional[int] = None
        for move in available:
            board[move] = ai_player
            score, _ = plain_minimax(
                board, depth + 1, False, ai_player, human_player, counter
            )
            board[move] = EMPTY
            if score > best_score:
                best_score = score
                best_move = move
        return int(best_score), best_move
    else:
        best_score = math.inf
        best_move = None
        for move in available:
            board[move] = human_player
            score, _ = plain_minimax(
                board, depth + 1, True, ai_player, human_player, counter
            )
            board[move] = EMPTY
            if score < best_score:
                best_score = score
                best_move = move
        return int(best_score), best_move


def minimax_alpha_beta(
    board: List[str],
    depth: int,
    alpha: float,
    beta: float,
    is_maximizing: bool,
    ai_player: str,
    human_player: str,
    counter: Dict[str, int],
) -> Tuple[int, Optional[int]]:
    """
    Minimax algorithm enhanced with Alpha-Beta Pruning.
    Prunes branches that cannot influence the final decision.
    Returns (score, best_move).
    """
    counter["nodes"] += 1

    winner = _quick_check_winner(board)
    if winner == ai_player:
        return 10 - depth, None
    if winner == human_player:
        return depth - 10, None

    available = [i for i, cell in enumerate(board) if cell == EMPTY]
    if not available:
        return 0, None  # Draw

    if is_maximizing:
        best_score = -math.inf
        best_move: Optional[int] = None
        for move in available:
            board[move] = ai_player
            score, _ = minimax_alpha_beta(
                board, depth + 1, alpha, beta, False, ai_player, human_player, counter
            )
            board[move] = EMPTY
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break  # Beta cut-off
        return int(best_score), best_move
    else:
        best_score = math.inf
        best_move = None
        for move in available:
            board[move] = human_player
            score, _ = minimax_alpha_beta(
                board, depth + 1, alpha, beta, True, ai_player, human_player, counter
            )
            board[move] = EMPTY
            if score < best_score:
                best_score = score
                best_move = move
            beta = min(beta, best_score)
            if beta <= alpha:
                break  # Alpha cut-off
        return int(best_score), best_move


def compute_ai_move(
    game: TicTacToe,
    difficulty: str = DIFFICULTY_HARD,
    ai_player: str = PLAYER_O,
) -> Optional[AIMoveResult]:
    """
    Calculates the AI move, benchmarks both Minimax variants for node counts,
    and applies difficulty rules:
    - Easy: Completely random move.
    - Medium: 50% optimal move, 50% random move.
    - Hard: 100% optimal move (unbeatable).
    """
    available = game.available_moves()
    if not available:
        return None

    human_player = PLAYER_X if ai_player == PLAYER_O else PLAYER_O

    # 1. Run Minimax with Alpha-Beta Pruning
    ab_counter = {"nodes": 0}
    board_copy_ab = list(game.board)
    t0_ab = time.perf_counter()
    ab_score, ab_best_move = minimax_alpha_beta(
        board_copy_ab,
        0,
        -math.inf,
        math.inf,
        True,
        ai_player,
        human_player,
        ab_counter,
    )
    t1_ab = time.perf_counter()
    ab_duration_ms = (t1_ab - t0_ab) * 1000.0

    # Fallback if best_move wasn't assigned (e.g., only 1 move left)
    if ab_best_move is None or ab_best_move not in available:
        ab_best_move = available[0]

    # 2. Run Plain Minimax for comparison benchmark
    plain_counter = {"nodes": 0}
    board_copy_plain = list(game.board)
    t0_p = time.perf_counter()
    p_score, p_best_move = plain_minimax(
        board_copy_plain,
        0,
        True,
        ai_player,
        human_player,
        plain_counter,
    )
    t1_p = time.perf_counter()
    plain_duration_ms = (t1_p - t0_p) * 1000.0

    # Calculate pruning efficiency
    p_nodes = plain_counter["nodes"]
    ab_nodes = ab_counter["nodes"]
    if p_nodes > 0:
        reduction_percentage = ((p_nodes - ab_nodes) / p_nodes) * 100.0
    else:
        reduction_percentage = 0.0

    # 3. Determine move according to difficulty
    if difficulty == DIFFICULTY_EASY:
        chosen_move = random.choice(available)
    elif difficulty == DIFFICULTY_MEDIUM:
        # 50% optimal, 50% random
        if random.random() < 0.5:
            chosen_move = random.choice(available)
        else:
            chosen_move = ab_best_move
    else:  # DIFFICULTY_HARD
        chosen_move = ab_best_move

    return AIMoveResult(
        chosen_move=chosen_move,
        difficulty=difficulty,
        plain_nodes=p_nodes,
        ab_nodes=ab_nodes,
        ab_best_move=ab_best_move,
        reduction_percentage=max(0.0, reduction_percentage),
        ab_duration_ms=ab_duration_ms,
        plain_duration_ms=plain_duration_ms,
        eval_score=ab_score,
    )
