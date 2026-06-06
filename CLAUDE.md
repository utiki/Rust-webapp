# AI Assistant Instructions

<!-- 使用する言語のセクションだけ残して、不要なセクションは削除してください -->

---

## 🦀 Rust

- Edition: Rust 2021
- Formatter: `rustfmt`、Linter: `clippy`（警告はすべて解消）
- エラーは `anyhow` / `thiserror` で扱う（`unwrap()` は原則禁止）
- 非同期処理は `tokio` を使用
- `pub` な関数・構造体には必ずドキュメントコメント (`///`) を書く
- `unsafe` を使う場合は理由と安全性の根拠を記述する
- テストは `#[cfg(test)]` モジュールと `tests/` ディレクトリに分けて書く

---

## 🐍 Python

- Python 3.11+
- Formatter: `ruff format`、Linter: `ruff check`、型チェック: `mypy --strict`
- 型アノテーションを必ずつける（`X | None` 記法を使う）
- `dataclass` または `pydantic.BaseModel` でデータ構造を定義する
- 例外は具体的な型で捕捉する（`except Exception` は原則禁止）
- パッケージ管理は `uv`、依存関係は `pyproject.toml` で管理
- テストは `pytest`、カバレッジ80%以上を目標

---

## 🌐 JavaScript / HTML / CSS

- JavaScript: ES2022+（`import/export` を使用）
- `var` は使わない。`const` を基本とし、再代入が必要な場合のみ `let`
- 非同期処理は `async/await`、エラーは `try/catch` で処理
- HTML: セマンティックタグを使う（`<header>`, `<main>`, `<section>` など）
- すべての `<img>` に `alt` 属性、フォームには `<label>` を紐付ける
- CSS: カスタムプロパティで色・フォント・スペースを管理
- レイアウトは Flexbox / Grid（`float` は禁止）、モバイルファーストで書く
- Formatter: `Prettier`、Linter: `ESLint`
- テストは `Vitest` または `Jest`