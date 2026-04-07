# システムアーキテクチャ

## 全体構成

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                        │
│                                                          │
│  ┌──────────────────┐      ┌──────────────────────────┐ │
│  │   Frontend       │      │   Backend                │ │
│  │   React + Vite   │◄────►│   Python + FastAPI       │ │
│  │   :3000          │      │   :8000                  │ │
│  │                  │  WS  │                          │ │
│  │  Zustand (state) │◄────►│  インメモリストア         │ │
│  └──────────────────┘      └──────────────────────────┘ │
│                                                          │
│  Phase 2 予定:                                           │
│  ┌──────────┐   ┌──────────┐                            │
│  │ Redis    │   │PostgreSQL│                            │
│  │ (PubSub) │   │ (永続化) │                            │
│  └──────────┘   └──────────┘                            │
└─────────────────────────────────────────────────────────┘
```

---

## バックエンド設計

### ディレクトリ構造

```
backend/
├── Dockerfile
├── requirements.txt
└── app/
    ├── main.py              # FastAPIアプリ, CORSミドルウェア
    ├── store.py             # インメモリストア (games, ws_connections)
    ├── models/
    │   └── game.py          # Pydanticモデル (GameState, Request/Response)
    ├── services/
    │   ├── game_logic.py    # ゲームロジック (勝利判定, 状態遷移)
    │   └── cpu_ai.py        # CPUアルゴリズム
    └── routers/
        ├── game.py          # REST APIルーター
        └── ws.py            # WebSocketルーター
```

### REST API エンドポイント

| Method | Path | 説明 |
|--------|------|------|
| POST | `/api/games` | ゲーム作成 |
| GET | `/api/games/{game_id}` | ゲーム状態取得 |
| POST | `/api/games/{game_id}/give` | コマを相手に渡す |
| POST | `/api/games/{game_id}/place` | コマをボードに置く |
| GET | `/api/games/room/{room_code}` | ルームコードで参加 |
| GET | `/health` | ヘルスチェック |

### WebSocket

```
ws://host/ws/{game_id}/{player_number}
```

**受信メッセージ:**
```json
{ "action": "give", "piece_id": 5 }
{ "action": "place", "row": 2, "col": 3 }
```

**送信メッセージ:**
```json
{ "type": "state_update", "data": { ...GameState } }
{ "type": "error", "message": "..." }
{ "type": "player_disconnected", "player": 2 }
```

### ゲーム状態モデル

```python
class GameState:
    game_id: str
    mode: GameMode          # "cpu" | "local" | "online"
    cpu_level: CpuLevel     # "easy" | "medium" | "hard"
    board: list[list[int | None]]   # 4x4, None=空, 0-15=コマID
    available_pieces: list[int]     # 未使用コマのリスト
    current_player: int             # 1 or 2
    phase: GamePhase        # "give" | "place"
    selected_piece: int | None      # 渡されたコマ
    winner: int | None              # 1, 2, 0(引き分け), None(継続)
    winning_line: list[list[int]] | None  # [[row,col], ...]
    player2_ready: bool             # オンライン: P2参加済み
```

---

## フロントエンド設計

### ディレクトリ構造

```
frontend/src/
├── main.tsx                # エントリポイント
├── App.tsx                 # ルートコンポーネント
├── App.css
├── types/
│   └── game.ts             # 型定義, ユーティリティ関数
├── store/
│   └── gameStore.ts        # Zustand ストア (状態 + アクション)
└── components/
    ├── GameSetup.tsx        # モード選択 / ゲーム開始画面
    ├── Board.tsx            # 4x4ボード
    ├── Piece.tsx            # コマ (CSS属性表現)
    ├── PieceTray.tsx        # 残りコマ一覧
    └── GameInfo.tsx         # ターン情報 / 勝利表示
```

### 状態管理 (Zustand)

```typescript
interface UIState {
  game: GameState | null;
  hoveredPiece: number | null;
  hoveredCell: [number, number] | null;
  isLoading: boolean;
  error: string | null;
  playerNumber: 1 | 2;     // オンラインモード用
  socket: WebSocket | null;
}
```

### コンポーネント依存関係

```
App
├── GameSetup   (game === null)
└── [ゲーム中]
    ├── GameInfo     (ターン・フェーズ表示)
    ├── Board        (4x4グリッド)
    │   └── Piece    (各セルのコマ)
    └── PieceTray    (残りコマ)
        └── Piece    (クリック可能)
```

---

## CPU AI設計

### 難易度別アルゴリズム

| 難易度 | PLACE (置く場所) | GIVE (渡すコマ) |
|--------|-----------------|----------------|
| Easy | ランダム | ランダム |
| Medium | 即勝ちマスがあれば優先、なければランダム | 相手が即勝ちできないコマを優先 |
| Hard | ミニマックス (α-β枝刈り, 深さ4) | ミニマックス |

### ミニマックスの探索深さ

```
depth = min(4, 残りコマ数 × 2)
```

序盤は探索空間が広いため深さを制限。終盤は全探索に近づく。

---

## Phase 2 拡張計画

| 機能 | 実装方針 |
|------|----------|
| ユーザー認証 | JWT + PostgreSQL users テーブル |
| 対戦履歴 | PostgreSQL games/moves テーブル |
| オンライン対戦スケール | Redis Pub/Sub でWebSocketブロードキャスト |
| レーティング | Elo レーティングシステム |
