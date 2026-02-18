#!/bin/bash
# NewsSpY Batch Processing Script
# ローカル環境でバッチ処理を実行するためのスクリプト

cd "$(dirname "$0")"

# 一時ディレクトリの設定（ディスク容量不足対策）
mkdir -p tmp
export TMPDIR="$(pwd)/tmp"

# Cleanup function
cleanup() {
    echo ""
    echo "=========================================="
    echo "  🧹 Cleaning up..."
    echo "=========================================="

    # 一時ディレクトリのクリーンアップ
    if [ -d "tmp" ]; then
        echo "  Cleaning up temporary directory..."
        rm -rf tmp/* 2>/dev/null || true
        echo "  ✓ Temporary directory cleaned"
    fi

    echo "✓ Cleanup complete!"
}

trap cleanup EXIT INT TERM

# 仮想環境が存在するか確認
if [ ! -d "venv" ]; then
    echo "仮想環境が見つかりません。作成します..."
    python -m venv venv
fi

# 仮想環境をアクティベート
source venv/bin/activate

# 依存関係をインストール
pip install -q -r requirements.txt

# バッチ処理を実行
echo "バッチ処理を開始します..."
python batch/main.py

echo "バッチ処理が完了しました。"
