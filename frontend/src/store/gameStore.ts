import { create } from "zustand";
import type { GameState, GameMode, CpuLevel } from "../types/game";

// 開発・本番ともに相対URLを使用
// 開発: Vite の proxy が /api → backend:8000 に転送
// 本番: nginx が /api, /ws → backend に転送
const API = "/api/games";

function buildWsUrl(gameId: string, playerNumber: 1 | 2): string {
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${proto}//${window.location.host}/ws/${gameId}/${playerNumber}`;
}

interface UIState {
  game: GameState | null;
  hoveredPiece: number | null;
  hoveredCell: [number, number] | null;
  isLoading: boolean;
  error: string | null;
  playerNumber: 1 | 2;  // オンラインモード: 自分のプレイヤー番号
  socket: WebSocket | null;
}

interface UIActions {
  createGame: (mode: GameMode, cpuLevel: CpuLevel) => Promise<void>;
  joinGame: (roomCode: string) => Promise<void>;
  givePiece: (pieceId: number) => Promise<void>;
  placepiece: (row: number, col: number) => Promise<void>;
  setHoveredPiece: (id: number | null) => void;
  setHoveredCell: (cell: [number, number] | null) => void;
  resetGame: () => void;
  connectSocket: (gameId: string, playerNumber: 1 | 2) => void;
  disconnectSocket: () => void;
}

export const useGameStore = create<UIState & UIActions>((set, get) => ({
  game: null,
  hoveredPiece: null,
  hoveredCell: null,
  isLoading: false,
  error: null,
  playerNumber: 1,
  socket: null,

  createGame: async (mode, cpuLevel) => {
    set({ isLoading: true, error: null });
    try {
      const res = await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode, cpu_level: cpuLevel }),
      });
      if (!res.ok) throw new Error(await res.text());
      const game: GameState = await res.json();
      set({ game, isLoading: false, playerNumber: 1 });

      if (mode === "online") {
        get().connectSocket(game.game_id, 1);
      }
    } catch (e) {
      set({ error: String(e), isLoading: false });
    }
  },

  joinGame: async (roomCode) => {
    set({ isLoading: true, error: null });
    try {
      const res = await fetch(`${API}/room/${roomCode}`);
      if (!res.ok) throw new Error("ルームが見つかりません");
      const game: GameState = await res.json();
      set({ game, isLoading: false, playerNumber: 2 });
      get().connectSocket(game.game_id, 2);
    } catch (e) {
      set({ error: String(e), isLoading: false });
    }
  },

  givePiece: async (pieceId) => {
    const { game, socket } = get();
    if (!game) return;

    if (game.mode === "online" && socket) {
      socket.send(JSON.stringify({ action: "give", piece_id: pieceId }));
      return;
    }

    set({ isLoading: true, error: null });
    try {
      const res = await fetch(`${API}/${game.game_id}/give`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ piece_id: pieceId }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "エラーが発生しました");
      }
      const updated: GameState = await res.json();
      set({ game: updated, isLoading: false });
    } catch (e) {
      set({ error: String(e), isLoading: false });
    }
  },

  placepiece: async (row, col) => {
    const { game, socket } = get();
    if (!game) return;

    if (game.mode === "online" && socket) {
      socket.send(JSON.stringify({ action: "place", row, col }));
      return;
    }

    set({ isLoading: true, error: null });
    try {
      const res = await fetch(`${API}/${game.game_id}/place`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ row, col }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "エラーが発生しました");
      }
      const updated: GameState = await res.json();
      set({ game: updated, isLoading: false });
    } catch (e) {
      set({ error: String(e), isLoading: false });
    }
  },

  setHoveredPiece: (id) => set({ hoveredPiece: id }),
  setHoveredCell: (cell) => set({ hoveredCell: cell }),

  resetGame: () => {
    get().disconnectSocket();
    set({ game: null, error: null, hoveredPiece: null, hoveredCell: null });
  },

  connectSocket: (gameId, playerNumber) => {
    const wsUrl = buildWsUrl(gameId, playerNumber);
    const socket = new WebSocket(wsUrl);

    socket.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === "state_update") {
        set({ game: { ...get().game!, ...msg.data } });
      }
    };

    socket.onerror = () => set({ error: "WebSocket接続エラー" });
    set({ socket, playerNumber });
  },

  disconnectSocket: () => {
    get().socket?.close();
    set({ socket: null });
  },
}));
