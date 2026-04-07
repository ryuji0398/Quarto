# ---- ビルドステージ ----
FROM node:20-alpine AS builder

WORKDIR /app

# VITE_API_BASE_URL はビルド時に ARG で受け取る
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

COPY package.json .
RUN npm install

COPY . .
RUN npm run build

# ---- 本番ステージ ----
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
