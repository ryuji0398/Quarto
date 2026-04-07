"""
WebSocket ルーター (オンライン対戦用)

接続URL: ws://host/ws/{game_id}/{player_number}
メッセージ形式: JSON
"""
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.store import games, ws_connections
from app.models.game import GamePhase
from app.services.game_logic import apply_give, apply_place

router = APIRouter(tags=["websocket"])


async def broadcast(game_id: str, message: dict) -> None:
    """ゲームの全接続クライアントにメッセージを送信"""
    connections = ws_connections.get(game_id, [])
    dead = []
    for ws in connections:
        try:
            await ws.send_text(json.dumps(message))
        except Exception:
            dead.append(ws)
    for ws in dead:
        connections.remove(ws)


def game_state_payload(game_id: str) -> dict:
    state = games.get(game_id)
    if not state:
        return {"type": "error", "message": "ゲームが見つかりません"}
    return {
        "type": "state_update",
        "data": {
            "game_id": state.game_id,
            "board": state.board,
            "available_pieces": state.available_pieces,
            "current_player": state.current_player,
            "phase": state.phase,
            "selected_piece": state.selected_piece,
            "winner": state.winner,
            "winning_line": state.winning_line,
            "player2_ready": state.player2_ready,
        },
    }


@router.websocket("/ws/{game_id}/{player_number}")
async def websocket_endpoint(ws: WebSocket, game_id: str, player_number: int) -> None:
    state = games.get(game_id)
    if not state:
        await ws.close(code=4004)
        return

    await ws.accept()

    if game_id not in ws_connections:
        ws_connections[game_id] = []
    ws_connections[game_id].append(ws)

    if player_number == 2:
        state.player2_ready = True

    # 接続直後に現在の状態を送信
    await broadcast(game_id, game_state_payload(game_id))

    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            action = msg.get("action")

            if action == "give":
                piece_id = msg.get("piece_id")
                if piece_id is None:
                    continue
                ok, err = apply_give(state, piece_id)
                if not ok:
                    await ws.send_text(json.dumps({"type": "error", "message": err}))
                    continue

            elif action == "place":
                row, col = msg.get("row"), msg.get("col")
                if row is None or col is None:
                    continue
                ok, err = apply_place(state, row, col)
                if not ok:
                    await ws.send_text(json.dumps({"type": "error", "message": err}))
                    continue

            # 全クライアントに最新状態をブロードキャスト
            await broadcast(game_id, game_state_payload(game_id))

    except WebSocketDisconnect:
        ws_connections[game_id].remove(ws)
        await broadcast(game_id, {"type": "player_disconnected", "player": player_number})
