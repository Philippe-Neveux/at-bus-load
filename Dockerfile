FROM ghcr.io/astral-sh/uv:0.7.12-debian-slim

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

ADD . /app

WORKDIR /app
RUN uv sync --locked
 