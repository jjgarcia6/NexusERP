BACKEND_ENV=apps/backend/.env
FRONTEND_ENV=apps/frontend/.env

.PHONY: check-env dev stop lint test scan

check-env:
	@if [ ! -f $(BACKEND_ENV) ]; then echo "Missing $(BACKEND_ENV). Create it from apps/backend/.env.example"; exit 1; fi
	@if [ ! -f $(FRONTEND_ENV) ]; then echo "Missing $(FRONTEND_ENV). Create it from apps/frontend/.env.example"; exit 1; fi

dev: check-env
	docker compose up --build

stop:
	docker compose down

lint:
	docker compose run --rm backend ruff check .
	docker compose run --rm backend mypy .
	docker compose run --rm frontend npm run lint

test:
	docker compose run --rm backend pytest
	docker compose run --rm frontend npm run test

scan:
	docker compose run --rm backend bandit -r . -ll
	docker compose run --rm backend detect-secrets scan > /tmp/.secrets.baseline
	docker compose run --rm frontend npm audit --audit-level=high
