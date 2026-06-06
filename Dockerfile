# ============================================================
# Stage 1: ビルド環境
# ============================================================
FROM rust:slim AS builder

# 必要なシステムパッケージをインストール
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Node.js と Sass をインストール（Dart Sass の代わり）
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
      | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
      echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main" \
      > /etc/apt/sources.list.d/nodesource.list && \
      apt-get update && apt-get install -y nodejs && \
      npm install -g sass && \
      rm -rf /var/lib/apt/lists/*

# WASMターゲットを追加
RUN rustup target add wasm32-unknown-unknown

# cargo-leptos をプリビルドバイナリからインストール
RUN curl -L \
    https://github.com/leptos-rs/cargo-leptos/releases/download/v0.3.6/cargo-leptos-x86_64-unknown-linux-musl.tar.gz \
    -o /tmp/cargo-leptos.tar.gz && \
    tar -xzf /tmp/cargo-leptos.tar.gz -C /tmp/ && \
    find /tmp -name 'cargo-leptos' -type f -exec install -m 755 {} /usr/local/bin/cargo-leptos \; && \
    rm -f /tmp/cargo-leptos.tar.gz

# wasm-bindgen-cli をインストール
RUN cargo install wasm-bindgen-cli@0.2.106

WORKDIR /app

# 依存関係のキャッシュ（ソースより先にコピーしてキャッシュを活用）
COPY Cargo.toml Cargo.lock ./
RUN mkdir -p src && \
    echo "fn main() {}" > src/main.rs && \
    echo "pub fn placeholder() {}" > src/lib.rs && \
    cargo build --release --features ssr 2>/dev/null || true && \
    rm -rf src

# ソースコードをコピーしてビルド
COPY . .
RUN RUST_BACKTRACE=full cargo leptos build --release

# ============================================================
# Stage 2: 実行環境（最小イメージ）
# ============================================================
FROM debian:bookworm-slim AS runtime

RUN apt-get update && apt-get install -y \
    libssl3 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ビルド成果物をコピー
COPY --from=builder /app/target/release/web-app ./server
RUN mkdir -p target
COPY --from=builder /app/target/site ./target/site

# 静的ファイル
COPY --from=builder /app/public ./public

# 実行ユーザーを作成（root以外で実行）
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

ENV LEPTOS_OUTPUT_NAME="web-app"
ENV LEPTOS_SITE_ROOT="target/site"
ENV LEPTOS_SITE_PKG_DIR="pkg"
ENV LEPTOS_SITE_ADDR="0.0.0.0:3000"
ENV RUST_LOG="info"

EXPOSE 3000

CMD ["./server"]
