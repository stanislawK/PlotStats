COMPOSE_DEV=docker-compose -f docker-compose.yml

.PHONY: reports

reset-db:
	$(COMPOSE_DEV) rm -fsv postgres
	$(COMPOSE_DEV) up -d --force-recreate postgres

lint-backend:
	$(COMPOSE_DEV) run --rm --no-deps backend bash -c "\
		isort .;\
		black .;\
		flake8 .;\
	"

lint: lint-backend

test: test-backend

test-backend:
	$(COMPOSE_DEV) run --rm backend pytest .

psql:
	$(COMPOSE_DEV) exec postgres psql -U postgres

bash:
	$(COMPOSE_DEV) exec backend bash

setup:
	git config blame.ignoreRevsFile .git-blame-ignore-revs
	pre-commit install