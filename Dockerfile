# Dockerfile
# Image Docker pour l'agent local

FROM python:3.11-slim

WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY pyproject.toml .
RUN pip install --no-cache-dir -r <(cat pyproject.toml | grep -v "^\[project.scripts\]" | grep -v "^\[build-system\]" | grep -v "^\[tool.pytest")

# Copy agent code
COPY agent/ /app/agent/
COPY main.py /app/

# Create sandbox directory
RUN mkdir -p /tmp/agent

# Environment variables
ENV PYTHONPATH=/app
ENV SANDBOX_DIR=/tmp/agent

CMD ["python", "-m", "agent.main", "run"]