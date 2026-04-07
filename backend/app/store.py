"""
インメモリストア (Phase 1: DB未使用)
Phase 2でRedis/PostgreSQLに移行予定
"""
from typing import TYPE_CHECKING
from fastapi import WebSocket

if TYPE_CHECKING:
    from app.models.game import GameState

# game_id -> GameState
games: dict[str, "GameState"] = {}

# game_id -> List[WebSocket]
ws_connections: dict[str, list[WebSocket]] = {}
