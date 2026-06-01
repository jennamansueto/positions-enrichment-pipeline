FROM python:3.11-slim-bookworm

# Java 17 is required by PySpark / Delta Lake
RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-17-jre-headless && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Install uv for faster dependency management
RUN pip install uv

WORKDIR /app

# Copy dependency file first for caching
COPY pyproject.toml .
RUN uv pip install --system ".[dev]"

# Copy application code
COPY src/ src/
COPY config/ config/
COPY scripts/ scripts/

ENV PYTHONPATH=/app/src
ENV WAREHOUSE_PATH=/data/warehouse

ENTRYPOINT ["python", "-m", "enterprise_pipeline"]
