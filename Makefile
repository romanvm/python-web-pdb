.PHONY: test lint build clean

test:
	python tests/tests.py

lint:
	ruff check web_pdb/*.py

build:
	python -m build

clean:
	rm -rf build/ dist/ *.egg-info
