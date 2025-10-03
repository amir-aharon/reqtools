.PHONY: help run-server setup-dev test lint format build publish bump

help:
	@echo "Available targets:"
	@echo "  run-server    Start the FastAPI mock server"
	@echo "  setup-dev     Install all dependencies including dev dependencies"
	@echo "  test          Run tests with pytest"
	@echo "  lint          Run ruff and mypy checks"
	@echo "  format        Format code with black and ruff"
	@echo "  build         Build the package"
	@echo "  publish       Publish to PyPI"
	@echo "  bump          Bump version (usage: make bump PART=patch|minor|major)"
	@echo "  help          Show this help message"

run-server:
	uv run uvicorn reqtools.mock_server.server:app --reload --port 8000

setup-dev:
	uv sync --all-extras
	uv run pre-commit install
	
test:
	PYTHONPATH=. uv run pytest

lint:
	uv run isort --check-only .
	uv run black --check .
	uv run ruff check .
	uv run mypy .

format:
	uv run isort .
	uv run black .
	uv run ruff check --fix .

build:
	uv build

publish:
	uv publish

bump:
	uv run bump-my-version bump $(PART)