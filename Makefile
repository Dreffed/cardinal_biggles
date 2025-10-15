.PHONY: help install lint lint-fix test test-cov format clean setup-hooks

help:  ## Show this help message
	@echo "Cardinal Biggles - Development Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install Python dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

install-node:  ## Install Node.js dependencies (for markdown linting)
	npm install

setup-hooks:  ## Setup pre-commit hooks
	pip install pre-commit
	pre-commit install
	@echo "Pre-commit hooks installed!"

# Linting
lint:  ## Run all linters
	@echo "Running Python linters..."
	flake8 . --max-line-length=100 --extend-ignore=E203,W503
	@echo "Running markdown linter..."
	npm run lint:md

lint-fix:  ## Run linters with auto-fix
	@echo "Running Python formatters..."
	black . --line-length=100
	isort . --profile black --line-length 100
	@echo "Fixing markdown..."
	npm run lint:md:fix

lint-md:  ## Run markdown linter only
	npm run lint:md

lint-md-fix:  ## Fix markdown issues
	npm run lint:md:fix

# Testing
test:  ## Run all tests
	pytest

test-cov:  ## Run tests with coverage
	pytest --cov=. --cov-report=html --cov-report=term

test-unit:  ## Run unit tests only
	pytest -m unit

test-integration:  ## Run integration tests only
	pytest -m integration

# Formatting
format:  ## Format Python code
	black . --line-length=100
	isort . --profile black --line-length 100

# Cleaning
clean:  ## Clean up generated files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/

# Development
dev-setup:  ## Complete development setup
	$(MAKE) install
	$(MAKE) install-node
	$(MAKE) setup-hooks
	@echo ""
	@echo "Development environment ready!"
	@echo "Run 'make help' to see available commands"

# Research (for testing)
research-local:  ## Run local smoke test
	python -m cli.main research "Machine Learning" \
		--config config/local_ollama.yaml \
		--output reports/test_output.md

# Configuration
test-providers:  ## Test all LLM providers
	python -m cli.main test-providers --config config/config.yaml

show-config:  ## Show current configuration
	python -m cli.main show-config --config config/config.yaml

# Documentation
docs-check:  ## Check documentation for broken links
	@echo "Checking documentation..."
	@find . -name "*.md" -type f ! -path "./node_modules/*" ! -path "./venv/*" ! -path "./reports/*" -exec echo "Checking {}" \;

# Git
pre-commit:  ## Run pre-commit hooks manually
	pre-commit run --all-files

# Version management
version:  ## Show current version
	@python -c "import toml; print(toml.load('pyproject.toml')['project']['version'])"
