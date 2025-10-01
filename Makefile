.PHONY: help run-server

help:
	@echo "Available targets:"
	@echo "  run-server    Start the FastAPI mock server"
	@echo "  help          Show this help message"

run-server:
	uv run uvicorn mock_server.main:app --reload --port 8000