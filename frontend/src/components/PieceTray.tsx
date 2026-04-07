import { useGameStore } from "../store/gameStore";
import { Piece } from "./Piece";
import styles from "./PieceTray.module.css";

export function PieceTray() {
  const { game, hoveredPiece, setHoveredPiece, givePiece, playerNumber } = useGameStore();
  if (!game) return null;

  const { available_pieces, phase, winner, current_player, mode, selected_piece } = game;

  // 自分がコマを渡すターンか
  const isMyTurn =
    phase === "give" &&
    winner === null &&
    (mode !== "online" || current_player === playerNumber);

  return (
    <div className={styles.tray}>
      <h3 className={styles.title}>残りコマ ({available_pieces.length}個)</h3>
      <p className={styles.hint}>
        {isMyTurn
          ? "相手に渡すコマを選んでください"
          : phase === "place"
          ? "コマをボードに置いてください"
          : "相手のターン"}
      </p>
      <div className={styles.grid}>
        {available_pieces.map((id) => (
          <div key={id} className={styles.slot}>
            <Piece
              pieceId={id}
              size="sm"
              selected={selected_piece === id}
              highlighted={hoveredPiece === id}
              onClick={isMyTurn ? () => givePiece(id) : undefined}
              onMouseEnter={() => setHoveredPiece(id)}
              onMouseLeave={() => setHoveredPiece(null)}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
