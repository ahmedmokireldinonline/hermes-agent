.PHONY: install lint test up down pull-models audit
install:
	python -m pip install -r requirements-dev.txt
lint:
	ruff check app tests scripts
	ruff format --check app tests scripts
test:
	pytest -q --cov=app --cov-report=term-missing
up:
	cp -n .env.example .env || true
	docker compose up --build
down:
	docker compose down
pull-models:
	PROFILE=$${PROFILE:-lite} ./scripts/pull-models.sh
audit:
	pip-audit -r requirements.txt
