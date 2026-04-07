# 開発ガイド

## 起動方法

### 前提条件
- Docker Desktop がインストール済み

### 起動

```bash
cd Quarto
docker-compose up --build
```

- フロントエンド: http://localhost:3000
- バックエンド API: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs

### ホットリロード

- **バックエンド**: `uvicorn --reload` が有効。`backend/app/` 配下を変更すると自動再起動
- **フロントエンド**: Vite HMR が有効。`frontend/src/` 配下を変更すると自動更新

---

## ファイル別の役割

### バックエンド

| ファイル | 役割 |
|---------|------|
| `app/main.py` | FastAPIアプリ本体, CORSミドルウェア, ルーター登録 |
| `app/store.py` | インメモリの `games` dict と `ws_connections` dict |
| `app/models/game.py` | 全Pydanticモデル (GameState, Request, Response) |
| `app/services/game_logic.py` | ゲームルール実装 (apply_give, apply_place, check_win) |
| `app/services/cpu_ai.py` | Easy/Medium/Hard AIロジック |
| `app/routers/game.py` | REST APIエンドポイント |
| `app/routers/ws.py` | WebSocketエンドポイント (オンライン対戦) |

### フロントエンド

| ファイル | 役割 |
|---------|------|
| `src/types/game.ts` | TypeScript型定義, getPieceAttributes(), getPieceLabel() |
| `src/store/gameStore.ts` | Zustandストア (APIコール, WebSocket管理, UI状態) |
| `src/App.tsx` | セットアップ画面 ↔ ゲーム画面の切り替え |
| `src/components/GameSetup.tsx` | モード選択, ルーム作成/参加UI |
| `src/components/Board.tsx` | 4×4グリッド, コマ配置, 勝利ライン表示 |
| `src/components/Piece.tsx` | コマのビジュアル表現 (CSS属性) |
| `src/components/PieceTray.tsx` | 残りコマ一覧, コマ選択UI |
| `src/components/GameInfo.tsx` | ターン表示, フェーズ表示, 勝利表示 |

---

## ゲームフロー詳細

### フェーズ遷移

```
初期状態: current_player=1, phase="give"

[GIVEフェーズ]
  → ユーザーがPieceTrayからコマをクリック
  → POST /api/games/{id}/give { piece_id: X }
  → state.selected_piece = X
  → state.available_pieces からXを除外
  → state.current_player を切り替え (1→2 or 2→1)
  → state.phase = "place"

[PLACEフェーズ]
  → ユーザーがBoardのマスをクリック
  → POST /api/games/{id}/place { row: R, col: C }
  → state.board[R][C] = selected_piece
  → 勝利判定 → 勝利なら state.winner を設定
  → 引き分け判定
  → 継続なら state.phase = "give" (current_playerはそのまま)
```

### CPUの動き

CPUは常にPlayer 2として動作します。

```
Player1がGIVE → CPUがPLACE & GIVE → Player1がPLACE
```

CPUの動きはAPIレスポンスに即座に反映されます (非同期ではなく同期的に処理)。

---

## API 利用例

### ゲーム作成

```bash
curl -X POST http://localhost:8000/api/games \
  -H "Content-Type: application/json" \
  -d '{"mode": "cpu", "cpu_level": "medium"}'
```

### コマを渡す

```bash
curl -X POST http://localhost:8000/api/games/{game_id}/give \
  -H "Content-Type: application/json" \
  -d '{"piece_id": 7}'
```

### コマを置く

```bash
curl -X POST http://localhost:8000/api/games/{game_id}/place \
  -H "Content-Type: application/json" \
  -d '{"row": 0, "col": 0}'
```

---

## 今後の実装予定 (Phase 2)

### オンライン対戦の完全実装

現在: WebSocketの基盤実装済み、ルームコード発行/参加可能

次のステップ:
1. Redisを追加 (`docker-compose.yml` にredisサービス追加)
2. `app/store.py` をRedis接続に移行
3. `app/routers/ws.py` でRedis Pub/Subを使ったブロードキャスト

### データベース追加

1. `docker-compose.yml` にPostgreSQLサービス追加
2. SQLAlchemy + Alembicでマイグレーション管理
3. ゲーム終了時にDBへ保存

### ユーザー認証

1. FastAPI-Users または自前JWT実装
2. ゲスト対戦 → ログイン対戦 の段階的実装
