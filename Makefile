IMAGE ?= fleetlens:local
ENV_FILE ?= .env

.PHONY: build run ping check render email-dry-run test coverage lint format clean

build:
	podman build -t $(IMAGE) .

run:
	podman run --rm \
	  -v "$$PWD:/workspace:Z" \
	  -v "$$HOME/.ssh:/home/runner/.ssh:ro,Z" \
	  --env-file $(ENV_FILE) \
	  $(IMAGE) \
	  ./scripts/run-check.sh

ping:
	podman run --rm \
	  -v "$$PWD:/workspace:Z" \
	  -v "$$HOME/.ssh:/home/runner/.ssh:ro,Z" \
	  --env-file $(ENV_FILE) \
	  $(IMAGE) \
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

