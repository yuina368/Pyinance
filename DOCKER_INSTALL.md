# Dockerインストールガイド

## WSL (Windows Subsystem for Linux) 環境の場合

WSL環境では、Docker Desktop for Windowsをインストールするのが最も簡単です。

### 方法1: Docker Desktop for Windows（推奨）

1. **Docker Desktopをダウンロード**
   - 公式サイトからダウンロード: https://www.docker.com/products/docker-desktop/
   - Windows版をダウンロードしてインストール

2. **WSL 2の有効化**
   ```powershell
   # PowerShell（管理者権限）で実行
   wsl --install
   ```

3. **Docker Desktopの設定**
   - Docker Desktopを起動
   - Settings > General > "Use the WSL 2 based engine" を有効化
   - Settings > Resources > WSL Integration > "Enable integration with my default WSL distro" を有効化

4. **確認**
   ```bash
   docker --version
   docker-compose --version
   ```

### 方法2: WSL内にDockerを直接インストール

Docker Desktopを使用せず、WSL内にDockerを直接インストールする場合：

```bash
# 依存関係を更新
sudo apt-get update

# 必要なパッケージをインストール
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Dockerの公式GPGキーを追加
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Dockerリポジトリを設定
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker Engineをインストール
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Dockerサービスを起動
sudo service docker start

# ユーザーをdockerグループに追加（再ログインが必要）
sudo usermod -aG docker $USER

# 確認
docker --version
docker-compose --version
```

### 方法3: Docker Composeスタンドアロン

Docker Engineがすでにインストールされている場合、Docker Composeのみをインストール：

```bash
# 最新バージョンをダウンロード
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 実行権限を付与
sudo chmod +x /usr/local/bin/docker-compose

# バージョンを確認
docker-compose --version
```

## インストール後の確認

```bash
# Dockerのバージョンを確認
docker --version

# Docker Composeのバージョンを確認
docker-compose --version

# Dockerが実行中か確認
sudo service docker status
# または
sudo systemctl status docker
```

## トラブルシューティング

### "Permission denied" エラー

```bash
# ユーザーをdockerグループに追加
sudo usermod -aG docker $USER

# 再ログインが必要（または以下を実行）
newgrp docker
```

### Dockerサービスが起動しない

```bash
# Dockerサービスを起動
sudo service docker start

# または
sudo systemctl start docker

# 自動起動を有効化
sudo systemctl enable docker
```

### WSL 2が有効でない場合

```powershell
# PowerShell（管理者権限）で実行
wsl --install
```

## プロジェクトの実行

Dockerがインストールされたら、以下のコマンドでプロジェクトを実行できます：

```bash
cd /mnt/c/Users/User/Pyinance

# 環境変数を設定
cp .env.example .env
# .envファイルを編集してNewsAPIキーを設定

# Docker Composeで起動
docker-compose up -d

# ログを確認
docker-compose logs -f

# サービスを停止
docker-compose down
```

## 参考リンク

- [Docker公式ドキュメント](https://docs.docker.com/engine/install/debian/)
- [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
- [WSL 2のインストール](https://learn.microsoft.com/en-us/windows/wsl/install)
