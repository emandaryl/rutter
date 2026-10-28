# Fieldnote

A birding companion app: log field sightings, revisit them, and export them.
Personal hobby project — one user, one phone, a tiny hosted API.

## Run

```bash
npm install
npm start          # Expo dev server; press i / a to open iOS / Android
```

Native shells (`android/`, `ios/`) are Expo-managed. Regenerate them with
`expo run:android` / `expo run:ios` — do not flip project settings inside those
folders by hand.

## Shape

- `App.tsx` mounts a two-tab navigator (Home, Settings).
- Screens live in `src/screens/`, shared components in `src/components/`.
- All HTTP goes through `src/lib/apiClient.ts` (sole network entry point).
- Design tokens live in `src/theme/colors.ts`; screens never hardcode hex values.
- The backend is a separate deploy; there is no server code in this repo.
