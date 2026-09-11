# Platform pack: Rust

Detected by: `Cargo.toml` at repo root. This pack is a checklist of what to look for and how to phrase it — write what's actually found, not this pack's wording verbatim.

- **Tech Stack** — check `Cargo.toml` for: Rust edition (2021/2024); crate type (binary vs library vs multi-crate workspace); async runtime (`tokio`, `async-std`, or synchronous); web/networking framework (Axum, Actix-web, Rocket, Tonic for gRPC); database/ORM (`sqlx`, `diesel`, `sea-orm`); serialization (`serde`, `serde_json`); error handling (`thiserror` for library/domain errors, `anyhow`/`eyre` for application errors); CLI parsing (`clap`); test/benchmark framework (`cargo test`, `insta` snapshots, `criterion`).
- **Package Structure** — walk `src/` (or workspace `crates/` / `members = [...]`); typical files/modules: `main.rs` / `lib.rs`, `models/`, `handlers/`, `services/`, `db/`, `config.rs`, `errors.rs`.
- **Architecture Pattern** — describe ownership and data flow: request extraction (`State(...)` / extractors in Axum) → service/domain logic → persistence layer. Note concurrency and shared-state management (`Arc<T>`, `Arc<RwLock<T>>`, channels).
- **Data Layer Conventions** — if `sqlx`: compile-time verified queries (`sqlx::query!`), connection pool configuration, migration directory (`migrations/`). If `diesel`: `schema.rs` management, connection handling.
- **Coding Conventions** — check for: error propagation (`?` operator with typed errors), unwrap/expect policy (disallowed in production code, restricted to tests), concurrency safety patterns (`Send` + `Sync` bounds), structured tracing (`tracing::info!` with `tracing-subscriber` vs raw `println!`).
- **Domain Concepts** — read core `struct` and `enum` definitions for the domain noun hierarchy.
- **Conditional docs signals** — API.md if Axum/Actix route definitions or gRPC proto definitions exist; SECURITY.md if auth extractors, password hashing (argon2), or credential handling exists; DEPLOYMENT.md if Dockerfile, cross-compilation scripts, or release profiles in `Cargo.toml` exist; TESTING.md if unit tests (`#[cfg(test)]`) and integration tests in `tests/` exist.
