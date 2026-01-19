.PHONY: install lint format test check clean

install:
	poetry install
	poetry run pre-commit install

lint:
	poetry run ruff check .
	poetry run mypy .

format:
	poetry run ruff format .

test:
	poetry run pytest tests/

check: lint test

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
