.PHONY: setup test-r test-python lint coverage check-spec reproduce clean help

VENV := abc-venv/bin
PYTHON := $(VENV)/python
PIP := $(VENV)/pip
PYTEST := $(VENV)/pytest
RUFF := $(VENV)/ruff

# One-command complete setup
setup:
	@echo "Setting up ABC Assessment validation environment..."
	@echo "-> Installing R packages..."
	Rscript -e 'needed <- c("lavaan","semTools","simsem","psych","MASS","tidyverse"); \
		missing <- needed[!needed %in% installed.packages()[,"Package"]]; \
		if (length(missing) > 0) install.packages(missing, repos="https://cloud.r-project.org")'
	@echo "-> Creating Python virtual environment..."
	python3 -m venv abc-venv
	@echo "-> Installing Python packages..."
	$(PIP) install -r requirements.txt
	@echo "-> Setting up git hooks..."
	cp scripts/pre-commit .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
	@echo "-> Creating output directories..."
	mkdir -p outputs/reports outputs/plots outputs/datasets
	@echo "Setup complete."

# Run R validation only
test-r:
	@echo "Running R validation..."
	@if [ -f src/r_validation/02_abc_6factor_cfa.R ]; then \
		Rscript src/r_validation/02_abc_6factor_cfa.R; \
	else \
		echo "R validation script not yet created (Phase 0 pending)."; \
	fi

# Run Python tests only
test-python:
	$(PYTEST) tests/python_tests/ -v --tb=short

# Lint Python code
lint:
	$(RUFF) check src/ tests/
	$(RUFF) format --check src/ tests/

# Fix lint issues automatically
lint-fix:
	$(RUFF) check --fix src/ tests/
	$(RUFF) format src/ tests/

# Check test coverage
coverage:
	$(PYTEST) tests/python_tests/ --cov=src --cov-report=term-missing --cov-fail-under=85

# Check that all functions reference the spec
check-spec:
	$(PYTHON) scripts/check_spec_references.py

# Reproduce full validation from scratch (for external reviewers)
reproduce:
	@echo "Reproducing ABC validation..."
	@echo "--- Phase 0: R Validation ---"
	@$(MAKE) test-r
	@echo ""
	@echo "--- Phase A: Python Tests ---"
	@$(MAKE) test-python
	@echo ""
	@echo "Validation reproduced."

# Clean generated outputs
clean:
	rm -rf outputs/reports/* outputs/plots/* outputs/datasets/*
	rm -rf .pytest_cache __pycache__ .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned outputs."

# Show available commands
help:
	@echo "ABC Assessment Validation - Available Commands"
	@echo ""
	@echo "  make setup        - Install all dependencies and configure hooks"
	@echo "  make test-r       - Run R validation (Phase 0)"
	@echo "  make test-python  - Run Python tests (Phase A)"
	@echo "  make lint         - Check Python code style"
	@echo "  make lint-fix     - Auto-fix Python code style"
	@echo "  make coverage     - Run tests with coverage report"
	@echo "  make check-spec   - Verify spec references in code"
	@echo "  make reproduce    - Reproduce full validation end-to-end"
	@echo "  make clean        - Remove generated outputs"
