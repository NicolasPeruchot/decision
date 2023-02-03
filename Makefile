develop:
	pip install -e '.[dev]'
	pre-commit install

install:
	pip install -e .
	pre-commit install
