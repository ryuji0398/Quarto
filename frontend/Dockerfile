# ---- ビルドステージ ----
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .
RUN npm run build

# ---- 本番ステージ ----
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

# nginx が起動時に envsubst で ${BACKEND_URL} を置換する
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
