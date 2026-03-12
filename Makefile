.PHONY: help install lint format test test-all integration docker-up docker-down clean

PYTEST = python3 -m pytest
RUFF = ruff

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install in development mode with all dependencies
	pip install -e ".[dev]"
	pip install pytest-cov pre-commit tox
	pre-commit install

lint: ## Run linter and format checks
	$(RUFF) check sqlalchemy_cubrid/ test/
	$(RUFF) format --check sqlalchemy_cubrid/ test/

format: ## Auto-fix lint issues and format code
	$(RUFF) check --fix sqlalchemy_cubrid/ test/
	$(RUFF) format sqlalchemy_cubrid/ test/

test: ## Run offline tests with coverage (no DB required)
	$(PYTEST) test/ -v \
		--ignore=test/test_integration.py \
		--ignore=test/test_suite.py \
		--cov=sqlalchemy_cubrid \
		--cov-report=term-missing \
		--cov-fail-under=95

test-all: ## Run tests across all Python versions via tox
	tox

integration: docker-up ## Run integration tests against CUBRID Docker
	@echo "Waiting for CUBRID to be ready..."
	@sleep 10
	CUBRID_TEST_URL="cubrid://dba@localhost:33000/testdb" \
		$(PYTEST) test/test_integration.py -v
	$(MAKE) docker-down

docker-up: ## Start CUBRID Docker container
	docker compose up -d
	@echo "CUBRID container starting... Use 'docker compose logs -f' to monitor."

docker-down: ## Stop and remove CUBRID Docker container
	docker compose down -v

clean: ## Remove build artifacts and caches
	rm -rf build/ dist/ *.egg-info .pytest_cache/ .coverage .ruff_cache/ __pycache__/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
