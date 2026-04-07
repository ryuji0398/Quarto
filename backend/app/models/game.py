from __future__ import annotations
from enum import Enum
from pydantic import BaseModel
from typing import Optional


class GameMode(str, Enum):
    CPU = "cpu"
    LOCAL = "local"
    ONLINE = "online"


class GamePhase(str, Enum):
    GIVE = "give"    # 現在のプレイヤーが相手に渡すコマを選ぶ
    PLACE = "place"  # 現在のプレイヤーが受け取ったコマをボードに置く


class CpuLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class GameState(BaseModel):
    game_id: str
    mode: GameMode
    cpu_level: Optional[CpuLevel] = None
    # 4x4ボード: None = 空, 0-15 = コマID
    board: list[list[Optional[int]]]
    available_pieces: list[int]       # まだ使われていないコマのリスト
    current_player: int               # 1 or 2
    phase: GamePhase
    selected_piece: Optional[int]     # 相手に渡すために選ばれたコマ
    winner: Optional[int]             # 1, 2, or 0 (引き分け)
    winning_line: Optional[list[list[int]]]  # [[row,col], ...]
    player2_ready: bool = False       # オンラインモード: P2が参加済みか

    @classmethod
    def new_game(cls, game_id: str, mode: GameMode, cpu_level: Optional[CpuLevel] = None) -> "GameState":
        return cls(
            game_id=game_id,
            mode=mode,
            cpu_level=cpu_level,
            board=[[None] * 4 for _ in range(4)],
            available_pieces=list(range(16)),
            current_player=1,
            phase=GamePhase.GIVE,
            selected_piece=None,
            winner=None,
            winning_line=None,
        )


class CreateGameRequest(BaseModel):
    mode: GameMode
    cpu_level: Optional[CpuLevel] = CpuLevel.MEDIUM


class GivePieceRequest(BaseModel):
    piece_id: int


class PlacePieceRequest(BaseModel):
    row: int
    col: int


class GameResponse(BaseModel):
    game_id: str
    mode: GameMode
    cpu_level: Optional[CpuLevel]
    board: list[list[Optional[int]]]
    available_pieces: list[int]
    current_player: int
    phase: GamePhase
    selected_piece: Optional[int]
    winner: Optional[int]
    winning_line: Optional[list[list[int]]]
    player2_ready: bool
    room_code: Optional[str] = None  # オンラインモード用
