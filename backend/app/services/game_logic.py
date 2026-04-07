"""
クアルトのゲームロジック

コマの属性 (0-15, 4ビット):
  bit0 (1): 高さ  - 0=低い, 1=高い
  bit1 (2): 色    - 0=濃い, 1=薄い
  bit2 (4): 形    - 0=四角, 1=丸
  bit3 (8): 頭    - 0=中実, 1=中空
"""
from typing import Optional
from app.models.game import GameState, GamePhase, GameMode

# 勝利ラインの定義 (4×4ボード: 行4 + 列4 + 斜め2 = 10ライン)
WINNING_LINES: list[list[tuple[int, int]]] = [
    # 横
    [(0,0),(0,1),(0,2),(0,3)],
    [(1,0),(1,1),(1,2),(1,3)],
    [(2,0),(2,1),(2,2),(2,3)],
    [(3,0),(3,1),(3,2),(3,3)],
    # 縦
    [(0,0),(1,0),(2,0),(3,0)],
    [(0,1),(1,1),(2,1),(3,1)],
    [(0,2),(1,2),(2,2),(3,2)],
    [(0,3),(1,3),(2,3),(3,3)],
    # 斜め
    [(0,0),(1,1),(2,2),(3,3)],
    [(0,3),(1,2),(2,1),(3,0)],
]


def check_line_win(pieces: list[int]) -> bool:
    """4つのコマが1つ以上の属性を共有しているか確認"""
    common_ones = pieces[0] & pieces[1] & pieces[2] & pieces[3]
    common_zeros = (~pieces[0] & ~pieces[1] & ~pieces[2] & ~pieces[3]) & 0xF
    return bool(common_ones or common_zeros)


def check_win(board: list[list[Optional[int]]]) -> tuple[bool, Optional[list[list[int]]]]:
    """
    ボード全体の勝利判定。
    Returns: (is_win, winning_line_as_list_of_[row,col])
    """
    for line in WINNING_LINES:
        cells = [board[r][c] for r, c in line]
        if all(c is not None for c in cells):
            if check_line_win(cells):  # type: ignore[arg-type]
                return True, [[r, c] for r, c in line]
    return False, None


def check_draw(board: list[list[Optional[int]]], available_pieces: list[int]) -> bool:
    """引き分け判定: 全マスが埋まっていてコマが残っていない"""
    return len(available_pieces) == 0 and all(
        board[r][c] is not None for r in range(4) for c in range(4)
    )


def would_win_with_piece(board: list[list[Optional[int]]], row: int, col: int, piece_id: int) -> bool:
    """指定マスにコマを置いた場合に勝利するか確認"""
    board[row][col] = piece_id
    win, _ = check_win(board)
    board[row][col] = None
    return win


def get_empty_cells(board: list[list[Optional[int]]]) -> list[tuple[int, int]]:
    """空のマスを全て返す"""
    return [(r, c) for r in range(4) for c in range(4) if board[r][c] is None]


def apply_give(state: GameState, piece_id: int) -> tuple[bool, str]:
    """
    コマを選んで相手に渡す処理。
    Returns: (success, error_message)
    """
    if state.phase != GamePhase.GIVE:
        return False, "現在はコマを渡すフェーズではありません"
    if state.winner is not None:
        return False, "ゲームは既に終了しています"
    if piece_id not in state.available_pieces:
        return False, f"コマ{piece_id}は使用できません"

    state.selected_piece = piece_id
    state.available_pieces.remove(piece_id)

    # 相手のターンに切り替え
    state.current_player = 2 if state.current_player == 1 else 1
    state.phase = GamePhase.PLACE
    return True, ""


def apply_place(state: GameState, row: int, col: int) -> tuple[bool, str]:
    """
    コマをボードに置く処理。
    Returns: (success, error_message)
    """
    if state.phase != GamePhase.PLACE:
        return False, "現在はコマを置くフェーズではありません"
    if state.winner is not None:
        return False, "ゲームは既に終了しています"
    if not (0 <= row < 4 and 0 <= col < 4):
        return False, "無効なマスです"
    if state.board[row][col] is not None:
        return False, "そのマスは既に埋まっています"
    if state.selected_piece is None:
        return False, "置くコマが選ばれていません"

    state.board[row][col] = state.selected_piece
    placed_piece = state.selected_piece
    state.selected_piece = None

    # 勝利判定
    is_win, winning_line = check_win(state.board)
    if is_win:
        state.winner = state.current_player
        state.winning_line = winning_line
        return True, ""

    # 引き分け判定
    if check_draw(state.board, state.available_pieces):
        state.winner = 0  # 引き分け
        return True, ""

    # 次のフェーズへ (コマを渡すフェーズ, 同じプレイヤーが続けて渡す)
    state.phase = GamePhase.GIVE
    return True, ""
