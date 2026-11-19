"""
tests/test_ai.py
Comprehensive test suite verifying:
1. Proof that the AI never loses across all possible human openings (AI as O and AI as X).
2. Minimax vs Alpha-Beta Pruning equivalence and node reduction verification.
3. Game rules, winning lines, and terminal state correctness.
4. Difficulty behaviors (Easy, Medium, Hard).
"""

import math
import pytest
from game import (
    TicTacToe,
    PLAYER_X,
    PLAYER_O,
    EMPTY,
    WINNING_COMBINATIONS,
)
from ai import (
    plain_minimax,
    minimax_alpha_beta,
    compute_ai_move,
    DIFFICULTY_EASY,
    DIFFICULTY_MEDIUM,
    DIFFICULTY_HARD,
)


def play_all_human_responses(game: TicTacToe, ai_player: str, human_player: str):
    """
    Recursively tests all possible human moves.
    When it's human's turn, branch across every legal move.
    When it's AI's turn, AI plays optimal move using minimax_alpha_beta.
    Asserts that human never wins (AI must win or draw in 100% of outcomes).
    """
    winner, _ = game.check_winner()
    if winner is not None:
        assert winner != human_player, f"AI lost! Winning board state:\n{game}"
        return
    if game.is_full():
        return  # Draw - valid outcome

    if game.current_player == human_player:
        for move in game.available_moves():
            g_branch = game.clone()
            g_branch.make_move(move)
            play_all_human_responses(g_branch, ai_player, human_player)
    else:
        # AI's turn (optimal move)
        counter = {"nodes": 0}
        board_copy = list(game.board)
        _, best_move = minimax_alpha_beta(
            board_copy, 0, -math.inf, math.inf, True, ai_player, human_player, counter
        )
        assert best_move is not None, f"AI could not find a move on board:\n{game}"
        g_branch = game.clone()
        g_branch.make_move(best_move)
        play_all_human_responses(g_branch, ai_player, human_player)


# --- 1. UNBEATABLE PROOFS ---

def test_ai_never_loses_as_o_all_openings():
    """
    Test every possible human opening move (all 9 initial squares) when Human is X and AI is O.
    Recursively verifies that human can NEVER win under any branch.
    """
    for human_first_move in range(9):
        game = TicTacToe(starting_player=PLAYER_X)
        game.make_move(human_first_move)
        play_all_human_responses(game, ai_player=PLAYER_O, human_player=PLAYER_X)


def test_ai_never_loses_as_x_going_first():
    """
    Test when AI plays first as X.
    AI takes an optimal opening move, then explores all possible human response trees.
    Verifies that human can NEVER win.
    """
    game = TicTacToe(starting_player=PLAYER_X)
    # AI plays move 0 (or any optimal move)
    counter = {"nodes": 0}
    board_copy = list(game.board)
    _, ai_opening = minimax_alpha_beta(
        board_copy, 0, -math.inf, math.inf, True, PLAYER_X, PLAYER_O, counter
    )
    assert ai_opening is not None
    game.make_move(ai_opening)
    play_all_human_responses(game, ai_player=PLAYER_X, human_player=PLAYER_O)


# --- 2. ALGORITHM COMPARISON & NODE REDUCTION TESTS ---

def test_alpha_beta_pruning_reduces_nodes_and_preserves_score():
    """
    Verify that Alpha-Beta Pruning achieves the exact same optimal score as Plain Minimax
    while evaluating significantly fewer search nodes.
    """
    # Board with 1 move played: human took corner 0
    board = [EMPTY] * 9
    board[0] = PLAYER_X

    plain_counter = {"nodes": 0}
    p_score, p_move = plain_minimax(
        list(board), 0, True, PLAYER_O, PLAYER_X, plain_counter
    )

    ab_counter = {"nodes": 0}
    ab_score, ab_move = minimax_alpha_beta(
        list(board), 0, -math.inf, math.inf, True, PLAYER_O, PLAYER_X, ab_counter
    )

    # Identical evaluation score
    assert p_score == ab_score
    # Alpha-Beta must explore substantially fewer nodes
    assert ab_counter["nodes"] < plain_counter["nodes"]
    # Usually around ~2,788 vs ~59,705 (over 90% reduction)
    reduction = (plain_counter["nodes"] - ab_counter["nodes"]) / plain_counter["nodes"]
    assert reduction > 0.50, f"Expected > 50% node reduction, got {reduction:.2%}"


def test_compute_ai_move_metrics():
    """Verify compute_ai_move returns correct metrics and node comparisons."""
    game = TicTacToe()
    game.make_move(4)  # Human plays center

    result = compute_ai_move(game, difficulty=DIFFICULTY_HARD, ai_player=PLAYER_O)
    assert result is not None
    assert result.plain_nodes > result.ab_nodes
    assert result.reduction_percentage > 0.0
    assert result.chosen_move in game.available_moves()
    assert result.chosen_move == result.ab_best_move


# --- 3. GAME RULES & WINNING COMBINATIONS ---

@pytest.mark.parametrize("line", WINNING_COMBINATIONS)
def test_all_eight_winning_lines(line):
    """Ensure all 8 win lines (3 rows, 3 cols, 2 diagonals) are recognized with line indices."""
    game = TicTacToe()
    a, b, c = line
    game.board[a] = PLAYER_X
    game.board[b] = PLAYER_X
    game.board[c] = PLAYER_X
    winner, win_line = game.check_winner()
    assert winner == PLAYER_X
    assert win_line == line


def test_draw_condition():
    """Ensure full board without 3-in-a-row is detected as draw."""
    game = TicTacToe()
    # X O X
    # X O O
    # O X X
    game.board = [
        PLAYER_X, PLAYER_O, PLAYER_X,
        PLAYER_X, PLAYER_O, PLAYER_O,
        PLAYER_O, PLAYER_X, PLAYER_X,
    ]
    winner, win_line = game.check_winner()
    assert winner is None
    assert win_line is None
    assert game.is_full() is True
    assert game.is_terminal() is True


def test_invalid_moves_rejected():
    """Cannot overwrite an existing cell or play out of bounds."""
    game = TicTacToe()
    assert game.make_move(0) is True
    assert game.make_move(0) is False  # Already taken
    assert game.make_move(-1) is False
    assert game.make_move(9) is False


# --- 4. DIFFICULTY LEVEL BEHAVIORS ---

def test_difficulty_easy():
    """Easy difficulty should always choose a valid legal move."""
    game = TicTacToe()
    game.make_move(0)
    result = compute_ai_move(game, difficulty=DIFFICULTY_EASY, ai_player=PLAYER_O)
    assert result is not None
    assert result.chosen_move in game.available_moves()


def test_difficulty_medium():
    """Medium difficulty should always choose a valid legal move."""
    game = TicTacToe()
    game.make_move(4)
    result = compute_ai_move(game, difficulty=DIFFICULTY_MEDIUM, ai_player=PLAYER_O)
    assert result is not None
    assert result.chosen_move in game.available_moves()


def test_difficulty_hard_blocks_immediate_win():
    """On Hard, AI must immediately block human when human is about to win."""
    game = TicTacToe()
    # Human has cells 0 and 1 -> AI must pick 2 to block
    game.make_move(0, player=PLAYER_X)
    game.make_move(4, player=PLAYER_O)
    game.make_move(1, player=PLAYER_X)
    result = compute_ai_move(game, difficulty=DIFFICULTY_HARD, ai_player=PLAYER_O)
    assert result is not None
    assert result.chosen_move == 2


def test_difficulty_hard_takes_immediate_win():
    """On Hard, AI must immediately take the winning move if available."""
    game = TicTacToe()
    # AI has cells 3 and 4 -> AI must pick 5 to win
    game.board[3] = PLAYER_O
    game.board[4] = PLAYER_O
    game.board[0] = PLAYER_X
    game.board[1] = PLAYER_X
    result = compute_ai_move(game, difficulty=DIFFICULTY_HARD, ai_player=PLAYER_O)
    assert result is not None
    assert result.chosen_move == 5
