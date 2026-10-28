# Claude Code notes (human-written, keep small)

- Formatting: no Prettier in this repo; match the file you are editing instead.
- Never run `expo prebuild` — it trashes the native shells.
- Version bumps happen in `package.json` `version` AND BOTH `versionCode`/`versionName`
  in `android/app/build.gradle` together.
