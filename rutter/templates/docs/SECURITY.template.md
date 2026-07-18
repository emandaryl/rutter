# Security

<!-- Conditional — only created if the repo shows evidence of auth/session handling or sensitive
data (auth middleware, token storage, a users/credentials model, secrets/env handling). Replace
every [FILL: ...] with real content read from the repo. Delete this comment when done. -->

## Auth Model

[FILL: how authentication/authorization actually works — token type (session, JWT, OAuth), where
credentials are stored client-side and server-side, how a request gets authenticated.]

## Sensitive Data

[FILL: what data the system treats as sensitive (PII, payment info, health data, credentials) and
where/how it's stored — encryption at rest, secure storage APIs used, redaction in logs.]

## Secrets & Config

[FILL: how API keys/secrets are managed — env vars, a secrets manager, a `.env` pattern — and the
explicit rule: never commit secrets, never log them.]
