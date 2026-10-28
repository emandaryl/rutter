install:
	uv sync
	cd web && pnpm install

dev:
	cd api && uv run uvicorn app.main:app --reload &
	cd web && pnpm dev

fmt:
	uv run ruff format api
	cd web && pnpm exec prettier --write src

test:
	cd api && uv run pytest
	cd web && pnpm vitest run
