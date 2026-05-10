.PHONY: test lint build clean

test:
	python tests/tests.py

lint:
	pylint web_pdb/

build:
	python -m build

clean:
	rm -rf build/ dist/ *.egg-info
