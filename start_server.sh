#!/bin/bash

# NewsSpY サーバー起動スクリプト
# このスクリプトはDocker Composeを使用してNewsSpYサーバーを起動します

set -e

# 色の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 現在のディレクトリを確認
if [ ! -f "docker-compose.yml" ]; then
    log_error "docker-compose.ymlが見つかりません。プロジェクトのルートディレクトリで実行してください。"
    exit 1
fi

# .envファイルの存在確認
if [ ! -f ".env" ]; then
    log_warning ".envファイルが見つかりません。.env.exampleから作成します..."
    cp .env.example .env
    log_warning ".envファイルを作成しました。必要に応じて編集してください。"
fi

# Dockerが実行中か確認
if ! docker info > /dev/null 2>&1; then
    log_error "Dockerが実行されていません。Dockerを起動してください。"
    exit 1
fi

# 既存のコンテナを停止・削除
log_info "既存のコンテナを停止・削除中..."
docker-compose down 2>/dev/null || true

# 未使用のDockerリソースをクリーンアップ
log_info "未使用のDockerリソースをクリーンアップ中..."
docker system prune -f > /dev/null 2>&1 || true

# Docker Composeで起動
log_info "Docker Composeでサーバーを起動中..."
docker-compose up -d

# コンテナの起動を待機
log_info "コンテナの起動を待機中..."
sleep 5

# コンテナのステータスを確認
log_info "コンテナのステータスを確認中..."
docker-compose ps

# バックエンドのヘルスチェックを待機
log_info "バックエンドのヘルスチェックを待機中..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/api/health/ > /dev/null 2>&1; then
        log_success "バックエンドが正常に起動しました！"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -n "."
    sleep 2
done

echo ""

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    log_warning "バックエンドの起動に時間がかかっています。ログを確認してください。"
    log_info "バックエンドログ: docker-compose logs backend"
fi

# アクセス情報を表示
echo ""
echo "=========================================="
echo "  NewsSpY サーバーが正常に起動しました！"
echo "=========================================="
echo ""
echo "📱 アプリケーション:"
echo "   Frontend:  http://localhost:3000"
echo "   Main:      http://localhost"
echo ""
echo "🔧 API:"
echo "   Backend API:      http://localhost:8000/api/docs"
echo "   Health Check:     http://localhost:8000/api/health/"
echo ""
echo "📊 コンテナ:"
echo "   Backend:  newspy-backend (ポート8000)"
echo "   Frontend: newspy-frontend (ポート3000)"
echo "   Nginx:    newspy-nginx (ポート80, 443)"
echo ""
echo "🛑 サーバーを停止するには:"
echo "   docker-compose down"
echo ""
echo "📋 ログを確認するには:"
echo "   docker-compose logs -f"
echo ""
