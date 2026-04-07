import { useGameStore } from "../store/gameStore";
import { Piece } from "./Piece";
import styles from "./GameInfo.module.css";

export function GameInfo() {
  const { game, playerNumber } = useGameStore();
  if (!game) return null;

  const { current_player, phase, selected_piece, winner, mode } = game;

  const playerLabel = (n: number) => {
    if (mode === "cpu") return n === 1 ? "あなた" : "CPU";
    if (mode === "online") return n === playerNumber ? "あなた" : "相手";
    return `プレイヤー${n}`;
  };

  return (
    <div className={styles.info}>
      {winner === null ? (
        <>
          <div className={styles.turnBadge} data-player={current_player}>
            {playerLabel(current_player)} のターン
          </div>
          <div className={styles.phaseLabel}>
            {phase === "give" ? "渡すコマを選択" : "コマをボードに置く"}
          </div>
          {selected_piece !== null && (
            <div className={styles.selectedPiece}>
              <span>渡されたコマ</span>
              <Piece pieceId={selected_piece} size="sm" />
            </div>
          )}
        </>
      ) : (
        <div className={styles.result}>
          {winner === 0
            ? "引き分け！"
            : `${playerLabel(winner)} の勝利！`}
        </div>
      )}
    </div>
  );
}
