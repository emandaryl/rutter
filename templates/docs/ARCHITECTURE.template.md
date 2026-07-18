# Architecture

<!-- Always created. Deeper technical detail than AGENTS.md's "Architecture Pattern" paragraph —
this is where the full data-flow diagram, every layer's responsibility, and cross-cutting concerns
live. Replace every [FILL: ...] with real content read from the repo. Delete this comment when
done. -->

## System Shape

[FILL: expanded version of AGENTS.md's Architecture Pattern — every layer named, what owns state,
how data flows end to end (e.g. request → handler → data layer → response, or
event → store → view). Include a diagram if the codebase shows clear layering.]

## Key Data Flows

[FILL: the 2-4 most important flows in the system (e.g. auth flow, the core read/write path, a
background job pipeline) — enough detail that an agent can trace a bug through the real code
without re-deriving the flow from scratch each time.]

## Cross-Cutting Concerns

[FILL: things that touch many parts of the codebase at once — error handling strategy, caching,
background work/job scheduling, feature flags, config management. Only include what's actually
present.]
