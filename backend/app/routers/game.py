import uuid
from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.game import (
    GameState, GameMode, GamePhase,
    CreateGameRequest, GivePieceRequest, PlacePieceRequest, GameResponse
)
from app.services.game_logic import apply_give, apply_place
from app.services.cpu_ai import cpu_choose_cell, cpu_choose_piece
from app.store import games

router = APIRouter(prefix="/api/games", tags=["games"])
limiter = Limiter(key_func=get_remote_address)


def state_to_response(state: GameState, room_code: str | None = None) -> GameResponse:
    return GameResponse(
        game_id=state.game_id,
        mode=state.mode,
        cpu_level=state.cpu_level,
        board=state.board,
        available_pieces=state.available_pieces,
        current_player=state.current_player,
        phase=state.phase,
        selected_piece=state.selected_piece,
        winner=state.winner,
        winning_line=state.winning_line,
        player2_ready=state.player2_ready,
        room_code=room_code,
    )


@router.post("", response_model=GameResponse)
@limiter.limit("20/minute")
def create_game(request: Request, req: CreateGameRequest) -> GameResponse:
    game_id = str(uuid.uuid4())
    state = GameState.new_game(game_id, req.mode, req.cpu_level)
    room_code = game_id[:6].upper() if req.mode == GameMode.ONLINE else None
    games[game_id] = state
    return state_to_response(state, room_code)


@router.get("/{game_id}", response_model=GameResponse)
@limiter.limit("120/minute")
def get_game(request: Request, game_id: str) -> GameResponse:
    state = games.get(game_id)
    if not state:
        raise HTTPException(status_code=404, detail="ゲームが見つかりません")
    return state_to_response(state)


@router.post("/{game_id}/give", response_model=GameResponse)
@limiter.limit("60/minute")
def give_piece(request: Request, game_id: str, req: GivePieceRequest) -> GameResponse:
    state = games.get(game_id)
    if not state:
        raise HTTPException(status_code=404, detail="ゲームが見つかりません")

    ok, err = apply_give(state, req.piece_id)
    if not ok:
        raise HTTPException(status_code=400, detail=err)

    if state.mode == GameMode.CPU and state.current_player == 2 and state.phase == GamePhase.PLACE:
        _cpu_take_full_turn(state)
        if state.winner is None and state.current_player == 2 and state.phase == GamePhase.GIVE:
            _cpu_give_turn(state)

    return state_to_response(state)


@router.post("/{game_id}/place", response_model=GameResponse)
@limiter.limit("60/minute")
def place_piece(request: Request, game_id: str, req: PlacePieceRequest) -> GameResponse:
    state = games.get(game_id)
    if not state:
        raise HTTPException(status_code=404, detail="ゲームが見つかりません")

    ok, err = apply_place(state, req.row, req.col)
    if not ok:
        raise HTTPException(status_code=400, detail=err)

    if (
        state.mode == GameMode.CPU
        and state.winner is None
        and state.current_player == 2
        and state.phase == GamePhase.GIVE
    ):
        _cpu_give_turn(state)

    return state_to_response(state)


def _cpu_take_full_turn(state: GameState) -> None:
    row, col = cpu_choose_cell(state)
    apply_place(state, row, col)


def _cpu_give_turn(state: GameState) -> None:
    if state.winner is not None or not state.available_pieces:
        return
    piece = cpu_choose_piece(state)
    apply_give(state, piece)


@router.get("/room/{room_code}", response_model=GameResponse)
@limiter.limit("20/minute")
def join_by_room_code(request: Request, room_code: str) -> GameResponse:
    code = room_code.upper()
    for game_id, state in games.items():
        if game_id[:6].upper() == code and state.mode == GameMode.ONLINE:
            state.player2_ready = True
            return state_to_response(state, code)
    raise HTTPException(status_code=404, detail="ルームが見つかりません")
