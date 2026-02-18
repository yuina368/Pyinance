#!/bin/bash

set -e  # エラーが発生したらスクリプトを終了

# ディレクトリパスの設定（絶対パスを使用）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# 一時ディレクトリの設定（ディスク容量不足対策）
mkdir -p "$PROJECT_DIR/tmp"
export TMPDIR="$PROJECT_DIR/tmp"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}  📊 NewsSpY Dashboard Launcher${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}  Project: $PROJECT_DIR${NC}"
echo -e "${BLUE}  Backend: $BACKEND_DIR${NC}"
echo -e "${BLUE}  Frontend: $FRONTEND_DIR${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}\n"

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}[*] Shutting down...${NC}"
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ -n "$STREAMLIT_PID" ]; then
        kill $STREAMLIT_PID 2>/dev/null || true
    fi
    wait 2>/dev/null || true
    echo -e "${GREEN}✓ All services stopped${NC}"

    # 一時ディレクトリのクリーンアップ
    if [ -d "$PROJECT_DIR/tmp" ]; then
        echo -e "${YELLOW}[*] Cleaning up temporary directory...${NC}"
        rm -rf "$PROJECT_DIR/tmp"/* 2>/dev/null || true
        echo -e "${GREEN}✓ Temporary directory cleaned${NC}"
    fi

    # ログファイルのクリーンアップ（オプション）
    if [ -d "$BACKEND_DIR/logs" ]; then
        echo -e "${YELLOW}[*] Cleaning up log files...${NC}"
        rm -f "$BACKEND_DIR/logs/backend.log" 2>/dev/null || true
        echo -e "${GREEN}✓ Log files cleaned${NC}"
    fi

    # Streamlit credentialsのクリーンアップ（オプション）
    if [ -f "$HOME/.streamlit/credentials.toml" ]; then
        echo -e "${YELLOW}[*] Cleaning up Streamlit credentials...${NC}"
        rm -f "$HOME/.streamlit/credentials.toml" 2>/dev/null || true
        echo -e "${GREEN}✓ Streamlit credentials cleaned${NC}"
    fi
}

trap cleanup EXIT INT TERM

# 仮想環境のセットアップ
echo -e "${YELLOW}[*] Checking environment...${NC}"

# 仮想環境がなければ作成
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo -e "${YELLOW}  Creating virtual environment...${NC}"
    cd "$BACKEND_DIR"
    python3 -m venv venv --system-site-packages || {
        echo -e "${RED}  ✗ Failed to create virtual environment${NC}"
        exit 1
    }
    echo -e "${GREEN}  ✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}  ✓ Virtual environment exists${NC}"
fi

# 仮想環境のアクティベート
if [ -f "$BACKEND_DIR/venv/bin/activate" ]; then
    source "$BACKEND_DIR/venv/bin/activate"
else
    echo -e "${RED}  ✗ Virtual environment activation failed${NC}"
    exit 1
fi

# pipがインストールされているか確認
if ! command -v pip &> /dev/null; then
    echo -e "${YELLOW}  Installing pip...${NC}"
    python3 -m ensurepip --upgrade || {
        echo -e "${RED}  ✗ Failed to install pip${NC}"
        exit 1
    }
fi

# 依存関係のインストール（変更があった場合のみ）
# requirements.txtのチェックサムを比較して変更がない場合はスキップするロジックも考えられるが、
# pip install はすでにインストール済みなら高速なのでそのまま実行するが、出力を抑制する。
echo -e "${YELLOW}[*] Verifying dependencies...${NC}"

# Backend Requirements
if [ -f "$BACKEND_DIR/requirements.txt" ]; then
    pip install -r "$BACKEND_DIR/requirements.txt" -q > /dev/null 2>&1 || {
         echo -e "${RED}  ✗ Failed to install backend dependencies${NC}"
         # 失敗した場合は詳細を表示して終了
         pip install -r "$BACKEND_DIR/requirements.txt"
         exit 1
    }
fi

# Frontend/Root Requirements
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    pip install -r "$PROJECT_DIR/requirements.txt" -q > /dev/null 2>&1 || {
        echo -e "${RED}  ✗ Failed to install frontend dependencies${NC}"
        pip install -r "$PROJECT_DIR/requirements.txt"
        exit 1
    }
fi

echo -e "${GREEN}  ✓ Dependencies ready${NC}\n"

# 1️⃣ Batch Processing (データ更新)
echo -e "${YELLOW}[1/4] Running Batch Processing...${NC}"
cd "$BACKEND_DIR"
if python batch/main.py; then
    echo -e "${GREEN}✓ Batch processing completed${NC}\n"
else
    echo -e "${YELLOW}⚠ Batch processing failed, continuing with existing data${NC}\n"
fi

# 2️⃣ Start Backend API
echo -e "${YELLOW}[2/4] Starting Backend API...${NC}"

# logsディレクトリを作成
mkdir -p logs

# バックエンドサーバーを起動（ログを表示）
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend ready
echo -e "${YELLOW}  Waiting for backend to start...${NC}"
for i in {1..60}; do
    if python -c "import requests; r = requests.get('http://127.0.0.1:8000/api/health/', timeout=2); print('healthy' if r.status_code == 200 else 'failed')" 2>/dev/null | grep -q "healthy"; then
        echo -e "${GREEN}✓ Backend API running on port 8000${NC}"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${RED}✗ Backend failed to start${NC}"
        echo -e "${YELLOW}  Checking backend logs...${NC}"
        tail -20 logs/backend.log
        exit 1
    fi
    sleep 1
done

# 3️⃣ Start Frontend Dashboard
echo -e "${YELLOW}[3/4] Starting Frontend Dashboard...${NC}"
cd "$FRONTEND_DIR"

# Skip streamlit email prompt
mkdir -p ~/.streamlit
cat > ~/.streamlit/credentials.toml << 'EOF'
[general]
email = ""
EOF

streamlit run dashboard.py \
    --server.port=8502 \
    --server.address=0.0.0.0 \
    --logger.level=warning > /dev/null 2>&1 &
STREAMLIT_PID=$!

# Wait for frontend ready
echo -e "${YELLOW}  Waiting for frontend to start...${NC}"
for i in {1..20}; do
    if python -c "import requests; r = requests.get('http://127.0.0.1:8502', timeout=2); print('success' if r.status_code == 200 else 'failed')" 2>/dev/null | grep -q "success"; then
        echo -e "${GREEN}✓ Dashboard running on port 8502${NC}"
        break
    fi
    if [ $i -eq 20 ]; then
        echo -e "${YELLOW}⚠ Dashboard may still be starting...${NC}"
    fi
    sleep 1
done

# 4️⃣ Open browser
echo -e "${YELLOW}[4/4] Opening browser...${NC}"
sleep 1
if command -v xdg-open &> /dev/null; then
    xdg-open http://127.0.0.1:8502 2>/dev/null &
    echo -e "${GREEN}✓ Browser launched${NC}"
elif command -v open &> /dev/null; then
    open http://127.0.0.1:8502 2>/dev/null &
    echo -e "${GREEN}✓ Browser launched${NC}"
elif command -v cmd.exe &> /dev/null; then
    # WSL環境でWindowsのブラウザを開く
    cmd.exe /c start http://127.0.0.1:8502 2>/dev/null &
    echo -e "${GREEN}✓ Browser launched${NC}"
else
    echo -e "${YELLOW}⚠ Please open http://127.0.0.1:8502 manually${NC}"
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  ✓ NewsSpY is ready!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${BLUE}Homepage:${NC} http://127.0.0.1:8502"
echo -e "${BLUE}API:${NC}      http://127.0.0.1:8000/api"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}\n"

# Keep running
wait
