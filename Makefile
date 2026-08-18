.DEFAULT_GOAL := help
MPLBACKEND := Agg
export MPLBACKEND

.PHONY: help setup test lint fix lab notebooks lessons calc clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup:  ## Create the venv and install everything (incl. Jupyter)
	uv sync --extra notebooks

test:  ## Run the test suite and the docstring examples
	uv run pytest -q

lint:  ## Check style
	uv run ruff check .

fix:  ## Fix what can be fixed automatically
	uv run ruff check . --fix

lab:  ## Open Jupyter Lab on the lessons (they open as notebooks via jupytext)
	uv run jupyter lab lessons/

notebooks:  ## Convert the lessons to .ipynb files (usually unnecessary)
	uv run jupytext --to notebook lessons/*.py

lessons:  ## Run every lesson end to end, checking they all still work
	@for f in lessons/*.py; do \
		printf '%-40s' "$$f"; \
		uv run python "$$f" > /dev/null 2>&1 && echo "ok" || echo "FAILED"; \
	done

calc:  ## Start the interactive calculator
	uv run pymath repl

clean:  ## Remove generated plots and caches
	rm -rf plots .pytest_cache .ruff_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
