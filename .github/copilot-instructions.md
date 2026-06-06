# GitHub Copilot Instructions

<!-- 使用する言語のセクションだけ残して、不要なセクションは削除してください -->

---

## 🦀 Rust
- Use Rust 2021 edition
- Handle errors with `Result`; avoid `unwrap()` in production code
- Follow `clippy` recommendations; no warnings allowed
- Use `tokio` for async, `serde` for serialization
- Write `///` doc comments for all public APIs

---

## 🐍 Python
- Use Python 3.11+ with full type annotations (`X | None` syntax)
- Format with `ruff format`, lint with `ruff check`, type-check with `mypy --strict`
- Use `pytest` for testing, `pydantic` for data validation
- Use `uv` for dependency management

---

## 🌐 JavaScript / HTML / CSS
- Use ES2022+ with `import/export`; never use `var`
- Use `async/await` with `try/catch` for error handling
- Write semantic HTML5; always include `alt` on images
- Use CSS custom properties for design tokens
- Format with `Prettier`, lint with `ESLint`
- Test with `Vitest` or `Jest`