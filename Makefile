PYTHON ?= python3

.PHONY: bootstrap run ping check render email-dry-run test coverage lint format clean

bootstrap:
	PYTHON=$(PYTHON) ./scripts/bootstrap.sh

run:
	./scripts/run-check.sh

ping:
	./scripts/run-ping.sh

check: lint test

render:
	python -m fleetlens.cli render

email-dry-run:
	python -m fleetlens.cli email --dry-run

test:
	python -m pytest

coverage:
	python -m coverage run -m pytest
	python -m coverage report

lint:
	python -m ruff check .

format:
	python -m ruff format .

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage coverage.xml build dist *.egg-info
