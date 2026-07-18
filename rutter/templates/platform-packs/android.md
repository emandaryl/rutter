# Platform pack: Android

Detected by: `build.gradle`/`build.gradle.kts` at repo root or in an app module, plus an
`AndroidManifest.xml`. This pack is a checklist of what to look for and how to phrase it — write
what's actually found, not this pack's wording verbatim.

- **Tech Stack** — check `build.gradle(.kts)` for: Kotlin vs Java (and whether both coexist —
  signals a migration-in-progress convention), Jetpack Compose vs XML/ViewBinding, DI framework
  (Hilt/Dagger/Koin), async model (Coroutines+Flow vs RxJava — and whether both coexist), local DB
  (Room/Realm/SQLDelight), networking (Retrofit/Ktor/OkHttp), analytics/crash reporting (Firebase,
  Crashlytics, Sentry). Read `minSdkVersion`/`targetSdkVersion` for the Build config line.
- **Package Structure** — walk `src/main/java|kotlin/<root package>/`; typical top-level folders to
  expect: `di/`, `models/` or `data/`, `repositories/`, `service/` (foreground services if any),
  `ui/screens/`, `ui/components/`, `util/`, `viewmodel/` if not colocated with screens.
- **Architecture Pattern** — look for a Service → Activity/Fragment → ViewModel → Compose/View
  bridge if foreground services exist (common for apps with background tracking); otherwise
  describe the real layering found (single-Activity + Compose Navigation, or Fragment-based).
- **Data Layer Conventions** — if Room: DAO interfaces + entity classes, repository pattern. If
  Realm: check for stateless-DAO pattern (`Realm.getDefaultInstance().use {}`), whether managed
  objects are copied out (`copyFromRealm`) before crossing threads.
- **Coding Conventions** — check for: hybrid Java/Kotlin migration rule, RxJava→Coroutines bridging
  pattern, `@Preview` usage on Composables (and whether it looks mandatory — multiple
  light/dark/state previews per screen is a strong signal), string resources (`strings.xml`) vs a
  custom runtime-string-provider system, ProGuard/R8 rules implying obfuscation-sensitive code.
- **Domain Concepts** — read core Kotlin data classes / Realm-Java model classes for the domain
  noun hierarchy.
- **Conditional docs signals** — SECURITY.md if biometric auth, encrypted prefs, or a token/session
  manager is present; DEPLOYMENT.md if `fastlane/`, a Play Console config, or a release-signing
  Gradle config exists; UI.md if Compose theme files or a Material theme XML exist.
