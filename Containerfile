FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      ca-certificates \
      git \
      openssh-client \
      sshpass \
      tini \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY requirements.txt requirements-dev.txt ./
# hadolint ignore=DL3013
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt -r requirements-dev.txt

RUN mkdir -p /home/runner/.ssh

# Rootless Podman maps container root to the invoking user outside the VM.
# This keeps bind-mounted repo output and read-only SSH material usable.
# hadolint ignore=DL3002
USER root

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["./scripts/run-check.sh"]
