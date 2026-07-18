# Platform pack: Generic fallback

Used when no known platform (Android/iOS/React/Flutter) is detected — e.g. a backend service,
CLI tool, library, or a stack not yet covered by a dedicated pack. This pack is a checklist of what
to look for and how to phrase it — write what's actually found, not this pack's wording verbatim.

- **Tech Stack** — identify language + version from whatever manifest exists (`pyproject.toml`/
  `requirements.txt`, `Cargo.toml`, `go.mod`, `Gemfile`, `pom.xml`/`build.gradle` for JVM
  backends, etc.); framework if any (Django/FastAPI/Flask, Express/Nest, Actix/Axum, Spring); DB/
  ORM; async model; test framework; package manager.
- **Package Structure** — walk the top 2-3 levels of the primary source directory; note the
  entry-point file(s) (`main.py`, `main.go`, `src/index.ts`, `cmd/`, etc.) and how modules are
  organized (by layer — controllers/services/models — or by feature/domain).
- **Architecture Pattern** — describe the real request/execution flow: for a service, entry point
  → routing/handler → business logic → data layer → response; for a CLI, command parsing →
  dispatch → execution; for a library, the public API surface and its main internal collaborators.
- **Data Layer Conventions** — only if a DB/ORM/persistence layer is found — connection/session
  handling pattern, migration tool in use.
- **Coding Conventions** — check for: a linter/formatter config implying enforced style, an
  in-progress migration (two versions of a language/framework coexisting), a preferred pattern for
  a recurring task type evident from multiple similar call sites, a logging library already in
  house use (vs raw print/console statements) — document the wrapper and the "never call print/
  console directly" rule if one exists.
- **Domain Concepts** — read core model/entity/schema definitions for the domain noun hierarchy.
- **Conditional docs signals** — API.md if the project exposes any request-handling routes/RPC
  definitions; SECURITY.md if auth middleware, a users/credentials model, or secrets handling
  exists; DEPLOYMENT.md if a Dockerfile, CI deploy workflow, or IaC config (Terraform, etc.)
  exists; TESTING.md if a test directory/framework exists; UI.md only if the project has an actual
  UI layer (most backends/CLIs/libraries won't — omit it rather than forcing it).
