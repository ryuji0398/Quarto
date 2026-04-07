import { useGameStore } from "../store/gameStore";
import { Piece } from "./Piece";
import styles from "./Board.module.css";

export function Board() {
  const { game, hoveredPiece, setHoveredCell, placepiece } = useGameStore();
  if (!game) return null;

  const { board, phase, selected_piece, winner, winning_line, current_player, mode } = game;

  const winningCells = new Set(
    (winning_line ?? []).map(([r, c]) => `${r}-${c}`)
  );

  const canPlace = phase === "place" && winner === null && selected_piece !== null;

  const handleCellClick = (row: number, col: number) => {
    if (!canPlace) return;
    if (board[row][col] !== null) return;
    placepiece(row, col);
  };

  return (
    <div className={styles.boardWrapper}>
      <div className={styles.board}>
        {board.map((row, r) =>
          row.map((cell, c) => {
            const key = `${r}-${c}`;
            const isEmpty = cell === null;
            const isWinning = winningCells.has(key);
            const isHoverable = canPlace && isEmpty;

            return (
              <div
                key={key}
                className={[
                  styles.cell,
                  isWinning ? styles.winningCell : "",
                  isHoverable ? styles.hoverable : "",
                ]
                  .filter(Boolean)
                  .join(" ")}
                onClick={() => handleCellClick(r, c)}
                onMouseEnter={() => isHoverable && setHoveredCell([r, c])}
                onMouseLeave={() => setHoveredCell(null)}
              >
                {cell !== null ? (
                  <Piece
                    pieceId={cell}
                    size="md"
                    highlighted={isWinning}
                  />
                ) : (
                  isHoverable && selected_piece !== null && (
                    <div className={styles.ghostWrapper}>
                      <Piece pieceId={selected_piece} size="md" />
                    </div>
                  )
                )}
              </div>
            );
          })
        )}
      </div>

      {/* ボードの行・列ラベル */}
      <div className={styles.colLabels}>
        {["A", "B", "C", "D"].map((l) => (
          <span key={l}>{l}</span>
        ))}
      </div>
      <div className={styles.rowLabels}>
        {["1", "2", "3", "4"].map((l) => (
          <span key={l}>{l}</span>
        ))}
      </div>
    </div>
  );
}
