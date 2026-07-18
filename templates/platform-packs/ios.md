# Platform pack: iOS

Detected by: `*.xcodeproj`/`*.xcworkspace`, `Package.swift`, or a `Podfile` at repo root. This pack
is a checklist of what to look for and how to phrase it — write what's actually found, not this
pack's wording verbatim.

- **Tech Stack** — Swift version (from `Package.swift` or project settings); UIKit vs SwiftUI (and
  whether both coexist — signals a migration-in-progress convention); dependency manager (Swift
  Package Manager, CocoaPods, Carthage); concurrency model (Combine vs async/await — and whether
  both coexist); persistence (Core Data, SwiftData, Realm, GRDB); networking (URLSession-based,
  Alamofire); DI approach (manual init injection, a container library, or a framework like
  Swinject); analytics/crash reporting (Firebase, Crashlytics, Sentry).
- **Package Structure** — walk the main target's source folder; typical groups to expect:
  `Models/`, `Views/` or `Screens/`, `ViewModels/`, `Services/` or `Managers/`, `Networking/`,
  `Persistence/` or `Data/`, `Resources/` (assets, `.xcassets`, `Localizable.strings`).
- **Architecture Pattern** — look for MVVM (ViewModel classes + `@Published`/`@ObservedObject`),
  MVC (traditional UIKit view controllers owning logic directly), or a coordinator/router pattern
  for navigation. Describe what's actually present, not the platform default.
- **Data Layer Conventions** — if Core Data/SwiftData: `NSManagedObject`/`@Model` pattern, context
  handling (main vs background context), whether objects cross threads safely or get converted to
  plain structs first.
- **Coding Conventions** — check for: UIKit→SwiftUI migration rule, Combine→async/await migration
  rule, `#Preview` usage on SwiftUI views (and whether it looks mandatory), `Localizable.strings`/
  String Catalog vs hardcoded strings, force-unwrap (`!`) usage policy if evident from lint config
  (e.g. SwiftLint rules).
- **Domain Concepts** — read core model structs/classes for the domain noun hierarchy.
- **Conditional docs signals** — SECURITY.md if Keychain access, biometric auth (Face ID/Touch ID),
  or a token/session manager is present; DEPLOYMENT.md if `fastlane/`, an `.xcconfig` for
  release signing, or App Store Connect API config exists; UI.md if a design-token file, a
  SwiftUI theme/`Color`+`Font` extension set, or a `.xcassets` color set convention exists.
