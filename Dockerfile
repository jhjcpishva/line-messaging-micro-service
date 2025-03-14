FROM python:3.11-slim
LABEL org.opencontainers.image.source="https://github.com/jhjcpishva/line-messaging-micro-service"

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

# Run the application.
CMD ["uv", "run", "main.py"]
