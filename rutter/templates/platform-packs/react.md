# Platform pack: React / React Native / Next.js

Detected by: `package.json` with `react`, `react-native`, or `next` in dependencies. This pack is a
checklist of what to look for and how to phrase it — write what's actually found, not this pack's
wording verbatim.

- **Tech Stack** — JS vs TypeScript (and whether both coexist — signals a migration-in-progress
  convention); framework (plain React, Next.js App/Pages Router, React Native, Expo); state
  management (Redux/Redux Toolkit, Zustand, Jotai, React Query/TanStack Query, plain
  Context+hooks); styling (CSS Modules, Tailwind, styled-components, StyleSheet for RN); package
  manager (npm/yarn/pnpm, from the lockfile present); test runner (Jest, Vitest, React Testing
  Library, Detox for RN); build tool (Vite, Webpack, Metro for RN).
- **Package Structure** — walk `src/` (or `app/` for Next.js App Router); typical folders to
  expect: `components/`, `hooks/`, `pages/` or `app/` (routes), `services/` or `api/`, `store/` or
  `state/`, `types/`, `utils/`.
- **Architecture Pattern** — describe the real component/data-flow shape: component-based with
  hooks for local state, a global store for shared state, data-fetching layer (React Query/SWR vs
  manual `fetch`/`axios` + `useEffect`). Note server components/server actions if Next.js App
  Router is in use.
- **Data Layer Conventions** — client-side: local storage/IndexedDB/AsyncStorage (RN) access
  pattern; if there's a backend in the same repo, note its DB/ORM here too (Prisma, Drizzle, etc.).
- **Coding Conventions** — check for: JS→TS migration rule, class-component→hooks migration rule,
  Storybook stories on components (and whether it looks mandatory — a story per component/variant
  is a strong signal), an i18n library (`react-i18next`, `next-intl`, `FormatJS`) vs hardcoded
  strings, a component library / design-system package used before creating new UI primitives.
- **Domain Concepts** — read core TS types/interfaces or GraphQL/API schema for the domain noun
  hierarchy.
- **Conditional docs signals** — API.md if the repo also contains API routes/handlers (Next.js API
  routes, a separate `server/`/`api/` package, or GraphQL schema files); SECURITY.md if an auth
  library (NextAuth, Clerk, Firebase Auth, custom JWT middleware) is present; DEPLOYMENT.md if a
  Vercel/Netlify config, Dockerfile, or CI deploy workflow exists; UI.md if a theme/design-token
  file or a shared component library exists.
