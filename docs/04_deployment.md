# デプロイ手順 (Render)

## 前提条件
- GitHub アカウント
- Render アカウント (無料) → https://render.com

---

## Step 1: GitHub にプッシュ

```bash
cd /Users/noda_ryuji/Desktop/my_app/Quarto

git init
git add .
git commit -m "initial commit"

# GitHub でリポジトリを作成後:
git remote add origin https://github.com/<your-username>/quarto.git
git push -u origin main
```

> `.gitignore` により `.env` ファイルはコミットされません。

---

## Step 2: Render でバックエンドをデプロイ

1. Render ダッシュボード → **New** → **Web Service**
2. GitHub リポジトリを連携
3. 設定:
   - **Root Directory**: `backend`
   - **Runtime**: `Docker`
   - **Dockerfile Path**: `./Dockerfile`
4. **Environment Variables** を追加:
   | Key | Value |
   |-----|-------|
   | `ENVIRONMENT` | `production` |
   | `ALLOWED_ORIGINS` | *(Step 3 完了後に設定。JSON配列形式: `["https://quarto-frontend.onrender.com"]`)* |
5. **Create Web Service** をクリック
6. デプロイ完了後、表示されるURLをメモ
   - 例: `https://quarto-backend.onrender.com`

---

## Step 3: Render でフロントエンドをデプロイ

1. Render ダッシュボード → **New** → **Web Service**
2. 同じリポジトリを選択
3. 設定:
   - **Root Directory**: `frontend`
   - **Runtime**: `Docker`
   - **Dockerfile Path**: `./Dockerfile`
4. **Build Arguments** を追加:
   | Key | Value |
   |-----|-------|
   | `VITE_API_BASE_URL` | `https://quarto-backend.onrender.com` (Step 2 のURL) |
5. **Create Web Service** をクリック
6. デプロイ完了後のURLをメモ
   - 例: `https://quarto-frontend.onrender.com`

---

## Step 4: バックエンドの CORS を更新

Step 3 で取得したフロントエンドURLをバックエンドの環境変数に設定:

Render ダッシュボード → `quarto-backend` → **Environment** → 編集:

| Key | Value |
|-----|-------|
| `ALLOWED_ORIGINS` | `https://quarto-frontend.onrender.com` |

**Manual Deploy** または自動再デプロイを待つ。

---

## Step 5: 動作確認

```bash
# バックエンドのヘルスチェック
curl https://quarto-backend.onrender.com/health

# 期待するレスポンス:
# {"status":"ok"}
```

ブラウザで `https://quarto-frontend.onrender.com` にアクセスしてゲームを確認。

---

## Render 無料プランの制限事項

| 制限 | 内容 |
|------|------|
| スリープ | 15分間アクセスがないとサービスがスリープ。次のアクセス時に起動 (30秒〜1分かかる) |
| インメモリ | 再起動でゲームデータは消える (現在の仕様) |
| 月750時間 | 2サービス合計。無料枠内に収まる |

---

## トラブルシューティング

### CORS エラーが出る場合
- バックエンドの `ALLOWED_ORIGINS` にフロントエンドのURLが正確に入っているか確認
- `https://` の有無、末尾スラッシュなしが正しい形式

### フロントエンドが API に繋がらない場合
- `VITE_API_BASE_URL` が正しく設定されているか確認
- フロントエンドを **再ビルド**（Render の Manual Deploy）

### WebSocket が繋がらない場合
- Render は WebSocket をサポートしています
- `wss://` (HTTPS版WebSocket) が自動で使われます

---

## 独自ドメインを使う場合 (オプション)

1. Render ダッシュボード → サービス → **Custom Domains**
2. ドメインのDNSにRenderのCNAMEレコードを追加
3. SSL証明書は Render が自動発行 (Let's Encrypt)
4. `ALLOWED_ORIGINS` と `VITE_API_BASE_URL` を独自ドメインのURLに更新
