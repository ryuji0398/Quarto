"""
クアルトCPUAI

難易度:
  EASY   - ランダム
  MEDIUM - 即勝ちチェック + 危険コマ回避
  HARD   - ミニマックス (α-β枝刈り, 深さ制限)
"""
import random
from typing import Optional
from app.models.game import GameState, CpuLevel
from app.services.game_logic import (
    check_win, would_win_with_piece, get_empty_cells, check_line_win, WINNING_LINES
)


# ---- ユーティリティ ----

def can_piece_win_on_board(board: list[list[Optional[int]]], piece_id: int) -> bool:
    """与えられたコマを置いたとき、どこかに置いて勝てるか確認"""
    for r, c in get_empty_cells(board):
        if would_win_with_piece(board, r, c, piece_id):
            return True
    return False


def find_winning_cell(board: list[list[Optional[int]]], piece_id: int) -> Optional[tuple[int, int]]:
    """そのコマで勝てるマスを返す (なければNone)"""
    for r, c in get_empty_cells(board):
        if would_win_with_piece(board, r, c, piece_id):
            return (r, c)
    return None


def safe_pieces(board: list[list[Optional[int]]], available: list[int]) -> list[int]:
    """相手に渡しても即負けしないコマのリスト"""
    return [p for p in available if not can_piece_win_on_board(board, p)]


# ---- Easy AI ----

def easy_choose_piece(available: list[int]) -> int:
    return random.choice(available)


def easy_choose_cell(board: list[list[Optional[int]]], piece_id: int) -> tuple[int, int]:
    cells = get_empty_cells(board)
    return random.choice(cells)


# ---- Medium AI ----

def medium_choose_cell(board: list[list[Optional[int]]], piece_id: int) -> tuple[int, int]:
    # 即勝ちできるマスがあれば置く
    win_cell = find_winning_cell(board, piece_id)
    if win_cell:
        return win_cell
    return random.choice(get_empty_cells(board))


def medium_choose_piece(board: list[list[Optional[int]]], available: list[int]) -> int:
    safe = safe_pieces(board, available)
    if safe:
        return random.choice(safe)
    return random.choice(available)  # 全部危険なら仕方なくランダム


# ---- Hard AI (minimax) ----

MAX_DEPTH = 4  # 深さ制限 (コマ数が多い序盤は浅く探索)


def evaluate(board: list[list[Optional[int]]], available: list[int]) -> int:
    """盤面スコア (CPU視点: 正=有利)"""
    # 勝利済みかチェック
    win, _ = check_win(board)
    if win:
        return 0  # このノードに到達した時点では置いた側が勝ち (呼び出し元で反転)
    return 0


def minimax(
    board: list[list[Optional[int]]],
    available: list[int],
    depth: int,
    is_maximizing: bool,
    alpha: float,
    beta: float,
    phase: str,  # "place" or "give"
    piece_to_place: Optional[int],
) -> float:
    """
    ミニマックス (α-β枝刈り)
    is_maximizing=True → CPUが有利なスコアを最大化
    """
    # 終端条件
    win, _ = check_win(board)
    if win:
        # 直前の手で勝った → 直前のプレイヤーが勝ち
        return -10 + depth if is_maximizing else 10 - depth

    empty = get_empty_cells(board)
    if not empty or not available:
        return 0  # 引き分け

    if depth == 0:
        return 0

    if phase == "place" and piece_to_place is not None:
        # コマを置くフェーズ
        best = -float("inf") if is_maximizing else float("inf")
        for r, c in empty:
            board[r][c] = piece_to_place
            score = minimax(board, available, depth - 1, not is_maximizing, alpha, beta, "give", None)
            board[r][c] = None

            if is_maximizing:
                best = max(best, score)
                alpha = max(alpha, best)
            else:
                best = min(best, score)
                beta = min(beta, best)
            if beta <= alpha:
                break
        return best
    else:
        # コマを渡すフェーズ
        best = -float("inf") if is_maximizing else float("inf")
        for piece in available:
            remaining = [p for p in available if p != piece]
            score = minimax(board, remaining, depth - 1, not is_maximizing, alpha, beta, "place", piece)

            if is_maximizing:
                best = max(best, score)
                alpha = max(alpha, best)
            else:
                best = min(best, score)
                beta = min(beta, best)
            if beta <= alpha:
                break
        return best


def hard_choose_cell(board: list[list[Optional[int]]], piece_id: int, available: list[int]) -> tuple[int, int]:
    # まず即勝ちチェック
    win_cell = find_winning_cell(board, piece_id)
    if win_cell:
        return win_cell

    empty = get_empty_cells(board)
    best_score = -float("inf")
    best_cell = random.choice(empty)
    depth = min(MAX_DEPTH, len(available) * 2)

    for r, c in empty:
        board[r][c] = piece_id
        score = minimax(board, available, depth, False, -float("inf"), float("inf"), "give", None)
        board[r][c] = None
        if score > best_score:
            best_score = score
            best_cell = (r, c)

    return best_cell


def hard_choose_piece(board: list[list[Optional[int]]], available: list[int]) -> int:
    best_score = float("inf")
    best_piece = random.choice(available)
    depth = min(MAX_DEPTH, len(available) * 2)

    for piece in available:
        remaining = [p for p in available if p != piece]
        score = minimax(board, remaining, depth, True, -float("inf"), float("inf"), "place", piece)
        if score < best_score:
            best_score = score
            best_piece = piece

    return best_piece


# ---- パブリックAPI ----

def cpu_choose_cell(state: GameState) -> tuple[int, int]:
    """CPUがコマを置くマスを決定"""
    board = state.board
    piece = state.selected_piece
    available = state.available_pieces

    if state.cpu_level == CpuLevel.EASY:
        return easy_choose_cell(board, piece)
    elif state.cpu_level == CpuLevel.MEDIUM:
        return medium_choose_cell(board, piece)
    else:
        return hard_choose_cell(board, piece, available)


def cpu_choose_piece(state: GameState) -> int:
    """CPUが相手に渡すコマを決定"""
    board = state.board
    available = state.available_pieces

    if state.cpu_level == CpuLevel.EASY:
        return easy_choose_piece(available)
    elif state.cpu_level == CpuLevel.MEDIUM:
        return medium_choose_piece(board, available)
    else:
        return hard_choose_piece(board, available)
