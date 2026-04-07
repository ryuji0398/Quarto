import { useGameStore } from "./store/gameStore";
import { GameSetup } from "./components/GameSetup";
import { Board } from "./components/Board";
import { PieceTray } from "./components/PieceTray";
import { GameInfo } from "./components/GameInfo";
import "./App.css";

export default function App() {
  const { game, resetGame } = useGameStore();

  if (!game) {
    return (
      <div className="screen center">
        <GameSetup />
      </div>
    );
  }

  return (
    <div className="screen">
      <header className="header">
        <h1 className="logo">QUARTO</h1>
        <button className="resetBtn" onClick={resetGame}>
          メニューへ
        </button>
      </header>

      {game.mode === "online" && !game.player2_ready && (
        <div className="waitingBanner">
          友達を待っています... ルームコード: <strong>{game.room_code}</strong>
        </div>
      )}

      <div className="gameLayout">
        <div className="leftPanel">
          <GameInfo />
          {/* 渡すコマ: 現在選ばれているコマを表示 */}
        </div>
        <Board />
        <div className="rightPanel">
          <PieceTray />
        </div>
      </div>
    </div>
  );
}
