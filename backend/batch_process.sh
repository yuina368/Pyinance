#!/bin/bash
#
# NewsSpY バッチ処理スクリプト
# 使用法: ./batch_process.sh
#

set -e  # エラーが発生したらスクリプトを終了

# スクリプトのあるディレクトリの親ディレクトリをプロジェクトルートとして設定
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$SCRIPT_DIR"

# 一時ディレクトリの設定（ディスク容量不足対策）
mkdir -p "$PROJECT_DIR/tmp"
export TMPDIR="$PROJECT_DIR/tmp"

echo "=========================================="
echo "  📰 NewsSpY Batch Processing"
echo "=========================================="
echo "  Project Root: $PROJECT_DIR"
echo "  Backend Dir: $BACKEND_DIR"
echo ""

# Activate virtual environment
if [ -f "$BACKEND_DIR/venv/bin/activate" ]; then
    source "$BACKEND_DIR/venv/bin/activate"
    echo "  ✓ Virtual environment activated"
else
    echo "  ✗ Virtual environment not found at: $BACKEND_DIR/venv/bin/activate"
    exit 1
fi

# Run batch processor
echo ""
echo "  Running batch processor..."
python "$BACKEND_DIR/batch/main.py" || {
    echo "  ✗ Batch processor failed"
    exit 1
}

echo ""
echo "✓ Done!"
