.PHONY: test lint lint-fix build clean frontend-build-dev frontend-build frontend-watch frontend-lint

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

frontend-build-dev:
	cd frontend && npm run build-dev

frontend-build:
	cd frontend && npm run build

frontend-watch:
	cd frontend && npm run watch

frontend-lint:
	cd frontend && npm run lint
