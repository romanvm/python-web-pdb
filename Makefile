.PHONY: test lint lint-fix build clean

test:
	uv run tests/tests.py

lint:
	ruff check web_pdb/*.py

lint-fix:
	ruff format web_pdb/*.py && ruff check --fix web_pdb/*.py

build:
	python -m build

clean:
	rm -rf build/ dist/ *.egg-info
