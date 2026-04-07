export type GameMode = "cpu" | "local" | "online";
export type GamePhase = "give" | "place";
export type CpuLevel = "easy" | "medium" | "hard";

export interface GameState {
  game_id: string;
  mode: GameMode;
  cpu_level: CpuLevel | null;
  board: (number | null)[][];
  available_pieces: number[];
  current_player: 1 | 2;
  phase: GamePhase;
  selected_piece: number | null;
  winner: number | null;  // 1, 2, 0(draw)
  winning_line: [number, number][] | null;
  player2_ready: boolean;
  room_code: string | null;
}

/** コマの4属性を分解 */
export interface PieceAttributes {
  tall: boolean;    // bit0: false=低い, true=高い
  light: boolean;   // bit1: false=濃い, true=薄い
  round: boolean;   // bit2: false=四角, true=丸
  hollow: boolean;  // bit3: false=中実, true=中空
}

export function getPieceAttributes(pieceId: number): PieceAttributes {
  return {
    tall:   Boolean(pieceId & 1),
    light:  Boolean(pieceId & 2),
    round:  Boolean(pieceId & 4),
    hollow: Boolean(pieceId & 8),
  };
}

export function getPieceLabel(pieceId: number): string {
  const { tall, light, round, hollow } = getPieceAttributes(pieceId);
  return [
    tall ? "高" : "低",
    light ? "薄" : "濃",
    round ? "丸" : "角",
    hollow ? "空" : "実",
  ].join("");
}
