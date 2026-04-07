import { getPieceAttributes } from "../types/game";
import styles from "./Piece.module.css";

interface PieceProps {
  pieceId: number;
  size?: "sm" | "md" | "lg";
  selected?: boolean;
  highlighted?: boolean;
  onClick?: () => void;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
}

export function Piece({
  pieceId,
  size = "md",
  selected = false,
  highlighted = false,
  onClick,
  onMouseEnter,
  onMouseLeave,
}: PieceProps) {
  const { tall, light, round, hollow } = getPieceAttributes(pieceId);

  const classes = [
    styles.piece,
    styles[size],
    tall ? styles.tall : styles.short,
    light ? styles.light : styles.dark,
    round ? styles.round : styles.square,
    selected ? styles.selected : "",
    highlighted ? styles.highlighted : "",
    onClick ? styles.clickable : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div
      className={classes}
      onClick={onClick}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      title={`${tall ? "高" : "低"} ${light ? "薄" : "濃"} ${round ? "丸" : "角"} ${hollow ? "空" : "実"}`}
    >
      {hollow && <div className={styles.hollow} />}
    </div>
  );
}
