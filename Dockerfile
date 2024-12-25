FROM ghcr.io/astral-sh/uv:0.5.11-python3.13-bookworm-slim

LABEL org.opencontainers.image.authors="Jose Sanchez-Gallego, gallegoj@uw.edu"
LABEL org.opencontainers.image.source=https://github.com/sdss/lvmecp

WORKDIR /opt

COPY . lvmecp

ENV UV_COMPILE_BYTECODE=1
ENV ENV UV_LINK_MODE=copy

# Sync the project
RUN cd lvmecp && uv sync --frozen --no-cache

CMD ["/opt/lvmecp/.venv/bin/lvmecp", "actor", "start", "--debug"]
