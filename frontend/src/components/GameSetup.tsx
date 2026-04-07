import { useState } from "react";
import { useGameStore } from "../store/gameStore";
import type { CpuLevel } from "../types/game";
import styles from "./GameSetup.module.css";

export function GameSetup() {
  const { createGame, joinGame, isLoading, error } = useGameStore();
  const [cpuLevel, setCpuLevel] = useState<CpuLevel>("medium");
  const [roomCode, setRoomCode] = useState("");
  const [view, setView] = useState<"top" | "cpu" | "local" | "online-create" | "online-join">("top");

  return (
    <div className={styles.setup}>
      <h1 className={styles.title}>QUARTO</h1>
      <p className={styles.subtitle}>クアルト</p>

      {view === "top" && (
        <div className={styles.menu}>
          <button className={styles.btn} onClick={() => setView("cpu")}>
            CPU対戦
          </button>
          <button className={styles.btn} onClick={() => setView("local")}>
            ローカル対戦
          </button>
          <button className={styles.btn} onClick={() => setView("online-create")}>
            オンライン対戦
          </button>
        </div>
      )}

      {view === "cpu" && (
        <div className={styles.panel}>
          <h2>CPU対戦</h2>
          <div className={styles.levelSelect}>
            <span>難易度</span>
            {(["easy", "medium", "hard"] as CpuLevel[]).map((lv) => (
              <button
                key={lv}
                className={[styles.levelBtn, cpuLevel === lv ? styles.active : ""].join(" ")}
                onClick={() => setCpuLevel(lv)}
              >
                {lv === "easy" ? "かんたん" : lv === "medium" ? "ふつう" : "むずかしい"}
              </button>
            ))}
          </div>
          <button
            className={styles.startBtn}
            onClick={() => createGame("cpu", cpuLevel)}
            disabled={isLoading}
          >
            {isLoading ? "..." : "ゲームスタート"}
          </button>
          <button className={styles.back} onClick={() => setView("top")}>← 戻る</button>
        </div>
      )}

      {view === "local" && (
        <div className={styles.panel}>
          <h2>ローカル対戦</h2>
          <p className={styles.desc}>同じ画面で2人が交互に操作します</p>
          <button
            className={styles.startBtn}
            onClick={() => createGame("local", "medium")}
            disabled={isLoading}
          >
            {isLoading ? "..." : "ゲームスタート"}
          </button>
          <button className={styles.back} onClick={() => setView("top")}>← 戻る</button>
        </div>
      )}

      {view === "online-create" && (
        <div className={styles.panel}>
          <h2>オンライン対戦</h2>
          <p className={styles.desc}>ルームを作成して友達を招待</p>
          <button
            className={styles.startBtn}
            onClick={() => createGame("online", "medium")}
            disabled={isLoading}
          >
            {isLoading ? "..." : "ルーム作成"}
          </button>
          <div className={styles.divider}>または</div>
          <div className={styles.joinRow}>
            <input
              className={styles.input}
              placeholder="ルームコード (6文字)"
              value={roomCode}
              onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
              maxLength={6}
            />
            <button
              className={styles.joinBtn}
              onClick={() => joinGame(roomCode)}
              disabled={roomCode.length !== 6 || isLoading}
            >
              参加
            </button>
          </div>
          <button className={styles.back} onClick={() => setView("top")}>← 戻る</button>
        </div>
      )}

      {error && <p className={styles.error}>{error}</p>}
    </div>
  );
}
