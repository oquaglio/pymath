# Pass recipe arguments through as real positional args ($@) rather than
# splicing them into the command line — otherwise a token like `*` in
# `just rpn "3 4 + 2 *"` gets glob-expanded into filenames by the shell.
set positional-arguments

# Plots are written to files rather than shown, so nothing needs a display.
export MPLBACKEND := "Agg"

# Show available recipes
default:
    @just --list --unsorted

# Create the venv and install everything (Jupyter + gmpy2)
setup:
    uv sync --all-extras

# Run the test suite and the docstring examples
test:
    uv run pytest -q

# Check style
lint:
    uv run ruff check .

# Fix what can be fixed automatically
fix:
    uv run ruff check . --fix

# Open Jupyter Lab on the lessons (they open as notebooks via jupytext)
lab:
    uv run jupyter lab lessons/

# Open Jupyter Lab on your own workbook
workbook:
    uv run jupyter lab workbook/

# Convert the lessons to .ipynb files (usually unnecessary)
notebooks:
    uv run jupytext --to notebook lessons/*.py

# Run every lesson end to end, checking they all still work
lessons:
    #!/usr/bin/env bash
    for f in lessons/*.py; do
        printf '%-40s' "$f"
        if uv run python "$f" > /dev/null 2>&1; then echo "ok"; else echo "FAILED"; fi
    done

# Start the interactive calculator
calc:
    uv run pymath repl

# RPN stack calculator: just rpn, or just rpn "3 4 + 2 *"
rpn *TOKENS:
    uv run pymath rpn "$@"

# Solve an equation: just solve "x^2 - 5x + 6 = 0"
solve EQUATION:
    uv run pymath solve "$1"

# Graph functions: just plot "x^2" "2x+1"
plot +EXPRESSIONS:
    uv run pymath plot "$@"

# Full curve analysis with a graph: just analyse "x^3 - 3x"
analyse EXPRESSION:
    uv run pymath analyse "$1"

# Everything CI would run
check: lint test lessons

# Remove generated plots and caches
clean:
    rm -rf plots .pytest_cache .ruff_cache
    find . -name __pycache__ -type d -prune -exec rm -rf {} +
