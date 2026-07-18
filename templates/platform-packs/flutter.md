# Platform pack: Flutter

Detected by: `pubspec.yaml` with a `flutter` dependency. This pack is a checklist of what to look
for and how to phrase it — write what's actually found, not this pack's wording verbatim.

- **Tech Stack** — Dart SDK version (from `pubspec.yaml` `environment:`); state management
  (Provider, Riverpod, Bloc/Cubit, GetX, plain `setState`); local persistence (Hive, Isar, sqflite,
  `shared_preferences`, `SQLite` via Drift); networking (`http`, `dio`); DI approach (constructor
  injection, `get_it`, Riverpod providers as DI); navigation (`Navigator` 1.0/2.0, `go_router`,
  `auto_route`); analytics/crash reporting (Firebase, Sentry).
- **Package Structure** — walk `lib/`; typical folders to expect: `models/`, `screens/` or
  `views/` or `pages/`, `widgets/` (shared components), `services/` or `repositories/`,
  `providers/` or `blocs/` or `controllers/` (state layer, named per the state-management choice
  above), `utils/`.
- **Architecture Pattern** — describe the real shape: widget tree composition + the chosen state
  layer (Provider/Riverpod/Bloc) feeding `StatelessWidget`/`StatefulWidget` rebuilds, and how
  business logic is separated from widget code (or isn't, if it's mixed in directly).
- **Data Layer Conventions** — DB/storage access pattern (a repository wrapping the DB package,
  direct box/table access in widgets, code-generated models via `build_runner`/`freezed`/`json_
  serializable` if present).
- **Coding Conventions** — check for: `setState`→structured-state-management migration rule if a
  mix is visible, widget/golden tests in use (and whether they look mandatory), the ARB/`intl`
  localization system vs hardcoded strings, a shared widget library used before creating new UI
  primitives, null-safety patterns around platform-channel or JSON-decoded data.
- **Domain Concepts** — read core Dart model/entity classes (plain classes or `freezed` data
  classes) for the domain noun hierarchy.
- **Conditional docs signals** — SECURITY.md if `flutter_secure_storage`, biometric auth
  (`local_auth`), or a token/session manager is present; DEPLOYMENT.md if `fastlane/`, Codemagic/
  Bitrise config, or platform-specific release signing config exists; UI.md if a `ThemeData`
  definition or a design-token file exists.
