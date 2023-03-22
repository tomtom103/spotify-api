.PHONY: install
install: 
	poetry install --with dev
	poetry export --without-hashes --format=requirements.txt > requirements.txt

.PHONY: test
test:
	poetry run pytest -vv -s tests/

.PHONY: format
format:
	# remove unused imports
	poetry run autoflake -r --in-place --remove-all-unused-imports app tests
	# sort imports
	poetry run isort --profile black app tests
	# re-format code
	poetry run black app tests

.PHONY: type-check
type-check:
	poetry run mypy

.PHONY: format-check
format-check:
	poetry run black app tests --check

.PHONY: run-dev
run-dev:
	poetry run python -m app.main
