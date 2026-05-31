.PHONY: install test lint typecheck run build clean generate-data validate-schema help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync --all-extras

test: ## Run all tests
	uv run pytest tests/ -v --tb=short

test-unit: ## Run unit tests only
	uv run pytest tests/unit/ -v --tb=short

test-integration: ## Run integration tests only
	uv run pytest tests/integration/ -v --tb=short -m integration

lint: ## Run linter
	uv run ruff check src/ tests/

lint-fix: ## Run linter with auto-fix
	uv run ruff check --fix src/ tests/

typecheck: ## Run type checker
	uv run mypy src/enterprise_pipeline/

run: ## Run pipeline for today's date
	uv run python -m enterprise_pipeline run --date $$(date +%Y-%m-%d)

generate-data: ## Generate sample data
	uv run python scripts/generate_sample_data.py

validate-schema: ## Validate config schemas
	uv run python scripts/validate_schema.py

build: ## Build Docker image
	docker build -t enterprise-pipeline:latest .

clean: ## Clean generated artifacts
	rm -rf data/warehouse/ quality_reports/*.json
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
