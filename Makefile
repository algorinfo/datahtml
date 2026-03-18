
.PHONY: cov
cov:
	uv run pytest --cov-report=term-missing --cov-config=pyproject.toml --cov=datahtml --cov=tests

.PHONY: test
test:
	uv run pytest

.PHONY: docs-serve
docs-serve:
	uv run --group docs sphinx-autobuild docs docs/_build/html --port 9292 --watch ./
